from __future__ import annotations

from datetime import datetime, timezone
from statistics import mean, median
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Event, OddsLine, OddsSnapshot, Pick
from app.utils.odds_math import american_to_decimal, american_to_probability


IMMUTABLE_PICK_FIELDS = {
    "event_id",
    "league",
    "sport",
    "market",
    "selection",
    "line_taken",
    "odds_taken_american",
    "odds_taken_decimal",
    "book_taken",
    "implied_prob_taken",
    "snapshot_id_taken",
    "pick_type",
    "tier",
    "model_version",
    "strategy_version",
    "run_id",
    "published_at",
}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _latest_snapshot_for_event(db: Session, event_id: int) -> OddsSnapshot | None:
    return (
        db.execute(
            select(OddsSnapshot)
            .where(OddsSnapshot.event_id == event_id)
            .order_by(OddsSnapshot.captured_at.desc())
            .limit(1)
        )
        .scalars()
        .first()
    )


def publish_pick(
    db: Session,
    *,
    event: Event,
    market: str,
    selection: str,
    line_taken: float | None,
    book_taken: str | None,
    odds_taken_american: int | None,
    pick_type: str,
    tier: str | None,
    model_version: str | None,
    strategy_version: str | None,
    run_id: UUID | None,
) -> Pick:
    snapshot = _latest_snapshot_for_event(db, event.id)
    if snapshot is None:
        raise ValueError("No odds snapshot found for event")

    selected_line = None
    if odds_taken_american is None:
        q = select(OddsLine).where(
            OddsLine.event_id == event.id,
            OddsLine.snapshot_id == snapshot.id,
            OddsLine.market == market,
            OddsLine.selection == selection,
        )
        if book_taken:
            q = q.where(OddsLine.book == book_taken)
            selected_line = db.execute(q).scalar_one_or_none()
        else:
            selected_line = db.execute(q.order_by(OddsLine.odds_decimal.desc())).scalars().first()
        if selected_line is None:
            raise ValueError("No matching odds line found")
        odds_taken_american = selected_line.odds_american
        book_taken = selected_line.book
        if line_taken is None:
            line_taken = selected_line.line

    odds_taken_decimal = american_to_decimal(odds_taken_american)
    implied_prob_taken = american_to_probability(odds_taken_american)

    pick = Pick(
        published_at=_utcnow(),
        event_id=event.id,
        league=event.league,
        market=market,
        selection=selection,
        line_taken=line_taken,
        odds_taken_american=odds_taken_american,
        odds_taken_decimal=odds_taken_decimal,
        book_taken=book_taken or "manual",
        implied_prob_taken=implied_prob_taken,
        snapshot_id_taken=snapshot.id,
        pick_type=pick_type,
        tier=tier,
        model_version=model_version,
        strategy_version=strategy_version,
        run_id=run_id or uuid4(),
    )
    db.add(pick)
    db.commit()
    db.refresh(pick)
    return pick


def capture_close_for_league(db: Session, league: str) -> dict:
    now = _utcnow()
    picks = db.execute(
        select(Pick)
        .join(Event, Event.id == Pick.event_id)
        .where(Pick.league == league, Pick.close_snapshot_id.is_(None), Event.commence_time.is_not(None), Event.commence_time <= now)
    ).scalars()

    captured = 0
    skipped = 0
    for pick in picks:
        snapshot = _latest_snapshot_for_event(db, pick.event_id)
        if snapshot is None:
            skipped += 1
            continue
        line = db.execute(
            select(OddsLine)
            .where(
                OddsLine.event_id == pick.event_id,
                OddsLine.snapshot_id == snapshot.id,
                OddsLine.market == pick.market,
                OddsLine.selection == pick.selection,
            )
            .order_by(OddsLine.odds_decimal.desc())
        ).scalars().first()
        if line is None:
            skipped += 1
            continue

        pick.close_captured_at = now
        pick.close_snapshot_id = snapshot.id
        pick.close_book = line.book
        pick.close_odds_american = line.odds_american
        pick.close_odds_decimal = line.odds_decimal
        pick.implied_prob_close = line.implied_prob
        pick.clv_bps = (line.implied_prob - pick.implied_prob_taken) * 10000
        if pick.status == "open":
            pick.status = "closed"
        captured += 1

    db.commit()
    return {"captured": captured, "skipped": skipped}


class NbaResultsFetcher:
    def fetch_completed(self) -> list[dict]:
        return []



def settle_picks_for_league(db: Session, league: str, fetcher: NbaResultsFetcher | None = None) -> dict:
    fetcher = fetcher or NbaResultsFetcher()
    for item in fetcher.fetch_completed():
        event = db.execute(select(Event).where(Event.external_id == item["external_id"], Event.league == league)).scalar_one_or_none()
        if event is None:
            continue
        event.is_completed = True
        event.result = item.get("result")
        event.completed_at = _utcnow()

    picks = db.execute(
        select(Pick)
        .join(Event, Event.id == Pick.event_id)
        .where(Pick.league == league, Pick.settled_at.is_(None), Event.is_completed.is_(True))
    ).scalars()

    settled = 0
    skipped = 0
    for pick in picks:
        event = db.execute(select(Event).where(Event.id == pick.event_id)).scalar_one()
        outcome = event.result
        if outcome is None:
            skipped += 1
            continue

        if outcome == "void":
            pick.result = "void"
            pick.pnl_units = 0.0
            pick.status = "void"
        elif outcome == "push":
            pick.result = "push"
            pick.pnl_units = 0.0
            pick.status = "settled"
        elif pick.selection == outcome:
            pick.result = "win"
            pick.pnl_units = pick.odds_taken_decimal - 1
            pick.status = "settled"
        else:
            pick.result = "loss"
            pick.pnl_units = -1.0
            pick.status = "settled"

        pick.settled_at = _utcnow()
        settled += 1

    db.commit()
    return {"settled": settled, "skipped": skipped}


def metrics_summary(db: Session) -> dict:
    open_count = db.execute(select(func.count(Pick.pick_id)).where(Pick.status == "open")).scalar_one()
    settled = db.execute(select(Pick).where(Pick.settled_at.is_not(None))).scalars().all()
    clv_values = [p.clv_bps for p in settled if p.clv_bps is not None]
    pnl_values = [p.pnl_units for p in settled if p.pnl_units is not None]
    return {
        "count_open": open_count,
        "count_settled": len(settled),
        "mean_clv_bps": mean(clv_values) if clv_values else None,
        "median_clv_bps": median(clv_values) if clv_values else None,
        "mean_pnl_units": mean(pnl_values) if pnl_values else None,
    }


def clv_distribution(db: Session, bins: int) -> dict:
    values = [
        row[0]
        for row in db.execute(select(Pick.clv_bps).where(Pick.settled_at.is_not(None), Pick.clv_bps.is_not(None))).all()
    ]
    if not values:
        return {"bins": [], "count": 0}

    lower = min(values)
    upper = max(values)
    width = (upper - lower) / bins if upper != lower else 1
    out = []
    for idx in range(bins):
        start = lower + (idx * width)
        end = start + width
        if idx == bins - 1:
            count = len([v for v in values if start <= v <= end])
        else:
            count = len([v for v in values if start <= v < end])
        out.append({"start": start, "end": end, "count": count})
    return {"bins": out, "count": len(values)}
