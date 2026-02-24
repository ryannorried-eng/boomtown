from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import main
from app.models import Event, Job, OddsLine, OddsSnapshot, Pick
from app.db.base import Base
from app.db import session as session_module
from app.jobs.runner import run_job_once
from app.services.picks_lifecycle import capture_close_for_league, settle_picks_for_league

app = main.app




def setup_db() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return Session(engine)



def seed_event_with_snapshot(db: Session) -> tuple[Event, OddsSnapshot]:
    event = Event(
        league="nba",
        external_id="evt_1",
        home_team="Home",
        away_team="Away",
        commence_time=datetime.now(timezone.utc) - timedelta(hours=1),
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    snapshot = OddsSnapshot(
        event_id=event.id,
        league="nba",
        source="test",
        captured_at=datetime.now(timezone.utc) - timedelta(minutes=30),
        raw_payload_hash="h1",
        run_id=UUID("00000000-0000-0000-0000-000000000001"),
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    line = OddsLine(
        snapshot_id=snapshot.id,
        event_id=event.id,
        book="draftkings",
        market="h2h",
        selection="home",
        line=None,
        odds_american=-110,
        odds_decimal=1.9090909,
        implied_prob=0.5238095,
    )
    db.add(line)
    db.commit()
    return event, snapshot



def test_pick_immutability_publish_then_patch_rejected(monkeypatch):
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[session_module.get_db] = override_get_db
    monkeypatch.setattr(main, "engine", engine)

    with TestingSession() as db:
        seed_event_with_snapshot(db)

    with TestClient(app) as client:
        published = client.post(
            "/picks/publish",
            json={"event_id": 1, "market": "h2h", "selection": "home", "pick_type": "consensus"},
        )
        assert published.status_code == 200
        pick_id = published.json()["pick_id"]

        patched = client.patch(f"/picks/{pick_id}", json={"market": "spread"})
        assert patched.status_code == 400

    app.dependency_overrides.clear()



def test_close_capture_idempotency_and_clv():
    db = setup_db()
    event, snapshot = seed_event_with_snapshot(db)

    pick = Pick(
        published_at=datetime.now(timezone.utc) - timedelta(hours=2),
        event_id=event.id,
        league="nba",
        market="h2h",
        selection="home",
        line_taken=None,
        odds_taken_american=-110,
        odds_taken_decimal=1.9090909,
        book_taken="draftkings",
        implied_prob_taken=0.5238095,
        snapshot_id_taken=snapshot.id,
        pick_type="consensus",
        run_id=UUID("00000000-0000-0000-0000-000000000100"),
        status="open",
    )
    db.add(pick)
    db.commit()

    newer = OddsSnapshot(
        event_id=event.id,
        league="nba",
        source="test",
        captured_at=datetime.now(timezone.utc),
        raw_payload_hash="h2",
        run_id=UUID("00000000-0000-0000-0000-000000000002"),
    )
    db.add(newer)
    db.commit()
    db.refresh(newer)
    db.add(
        OddsLine(
            snapshot_id=newer.id,
            event_id=event.id,
            book="fanduel",
            market="h2h",
            selection="home",
            line=None,
            odds_american=-120,
            odds_decimal=1.8333333,
            implied_prob=0.5454545,
        )
    )
    db.commit()

    first = capture_close_for_league(db, "nba")
    persisted = db.execute(select(Pick).where(Pick.pick_id == pick.pick_id)).scalar_one()
    assert first["captured"] == 1
    assert round(persisted.clv_bps, 3) == round((0.5454545 - 0.5238095) * 10000, 3)

    second = capture_close_for_league(db, "nba")
    persisted_again = db.execute(select(Pick).where(Pick.pick_id == pick.pick_id)).scalar_one()
    assert second["captured"] == 0
    assert persisted_again.close_snapshot_id == persisted.close_snapshot_id



def test_settlement_pnl_for_win_loss_push():
    db = setup_db()
    event, snapshot = seed_event_with_snapshot(db)

    def mkpick(selection: str, odds_dec: float):
        return Pick(
            published_at=datetime.now(timezone.utc),
            event_id=event.id,
            league="nba",
            market="h2h",
            selection=selection,
            odds_taken_american=-110,
            odds_taken_decimal=odds_dec,
            book_taken="draftkings",
            implied_prob_taken=0.52,
            snapshot_id_taken=snapshot.id,
            pick_type="consensus",
            run_id=UUID("00000000-0000-0000-0000-000000000010"),
            status="closed",
        )

    win_pick = mkpick("home", 1.9)
    loss_pick = mkpick("away", 2.0)
    push_pick = mkpick("home", 1.8)
    db.add_all([win_pick, loss_pick, push_pick])
    db.commit()

    event.is_completed = True
    event.result = "home"
    db.commit()

    settle_picks_for_league(db, "nba")
    db.refresh(win_pick)
    db.refresh(loss_pick)
    assert win_pick.result == "win" and round(win_pick.pnl_units, 6) == 0.9
    assert loss_pick.result == "loss" and loss_pick.pnl_units == -1.0

    # Push scenario on second event
    event2 = Event(league="nba", external_id="evt_2", is_completed=True, result="push")
    db.add(event2)
    db.commit()
    db.refresh(event2)
    push_pick.event_id = event2.id
    push_pick.settled_at = None
    push_pick.result = None
    db.commit()

    settle_picks_for_league(db, "nba")
    db.refresh(push_pick)
    assert push_pick.result == "push" and push_pick.pnl_units == 0.0



def test_jobs_status_for_capture_close_and_settle():
    db = setup_db()
    event, snapshot = seed_event_with_snapshot(db)

    pick = Pick(
        published_at=datetime.now(timezone.utc),
        event_id=event.id,
        league="nba",
        market="h2h",
        selection="home",
        odds_taken_american=-110,
        odds_taken_decimal=1.9,
        book_taken="draftkings",
        implied_prob_taken=0.52,
        snapshot_id_taken=snapshot.id,
        pick_type="consensus",
        run_id=UUID("00000000-0000-0000-0000-000000000020"),
        status="open",
    )
    db.add(pick)
    db.commit()

    capture_job = run_job_once(db, "capture_close", lambda _: capture_close_for_league(db, "nba"))
    settle_job = run_job_once(db, "settle", lambda _: settle_picks_for_league(db, "nba"))

    persisted = db.execute(select(Job).where(Job.id.in_([capture_job.id, settle_job.id]))).scalars().all()
    assert all(job.status == "succeeded" for job in persisted)
    assert {job.name for job in persisted} == {"capture_close", "settle"}
