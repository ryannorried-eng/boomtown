from __future__ import annotations

from uuid import UUID

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.jobs.runner import run_job_once
from app.models import Job, OddsLine, OddsSnapshot
from app.services.odds_collector import NbaOddsCollector


SAMPLE_PAYLOAD = [
    {
        "id": "evt_1",
        "home_team": "Boston Celtics",
        "away_team": "Miami Heat",
        "commence_time": "2026-03-01T01:00:00Z",
        "bookmakers": [
            {
                "key": "draftkings",
                "markets": [
                    {
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Boston Celtics", "price": -120},
                            {"name": "Miami Heat", "price": 105},
                        ],
                    }
                ],
            }
        ],
    }
]


def make_db_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return Session(engine)


def test_poll_idempotency_same_payload_inserted_once(monkeypatch):
    db = make_db_session()
    collector = NbaOddsCollector(db)
    monkeypatch.setattr(collector, "collect", lambda: SAMPLE_PAYLOAD)

    first = collector.collect_and_store(league="nba", run_id=UUID("00000000-0000-0000-0000-000000000001"))
    second = collector.collect_and_store(league="nba", run_id=UUID("00000000-0000-0000-0000-000000000002"))

    snapshot_count = db.execute(select(OddsSnapshot)).scalars().all()
    line_count = db.execute(select(OddsLine)).scalars().all()

    assert first == {"snapshots": 1, "lines": 2}
    assert second == {"snapshots": 0, "lines": 0}
    assert len(snapshot_count) == 1
    assert len(line_count) == 2


def test_job_runner_success_status_and_meta():
    db = make_db_session()

    job = run_job_once(db, "poll_odds", lambda _: {"snapshots": 1, "lines": 2})
    persisted = db.execute(select(Job).where(Job.id == job.id)).scalar_one()

    assert persisted.status == "succeeded"
    assert persisted.ended_at is not None
    assert persisted.meta == {"snapshots": 1, "lines": 2}


def test_job_runner_failure_status_and_error():
    db = make_db_session()

    def explode(_):
        raise RuntimeError("boom")

    job = run_job_once(db, "poll_odds", explode)
    persisted = db.execute(select(Job).where(Job.id == job.id)).scalar_one()

    assert persisted.status == "failed"
    assert persisted.error == "boom"
    assert "traceback" in persisted.meta
