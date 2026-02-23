from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Event, OddsLine, OddsSnapshot

router = APIRouter(prefix="/odds", tags=["odds"])


@router.get("/latest")
def get_latest_odds(league: str = Query("nba"), db: Session = Depends(get_db)):
    if league.lower() != "nba":
        raise HTTPException(status_code=400, detail="Only nba league is supported")

    snapshot = db.execute(
        select(OddsSnapshot).where(OddsSnapshot.league == league).order_by(OddsSnapshot.captured_at.desc())
    ).scalar_one_or_none()
    if snapshot is None:
        return {"snapshot": None}

    line_count = db.execute(select(func.count(OddsLine.id)).where(OddsLine.snapshot_id == snapshot.id)).scalar_one()
    return {
        "snapshot": {
            "id": snapshot.id,
            "event_id": snapshot.event_id,
            "source": snapshot.source,
            "captured_at": snapshot.captured_at,
            "run_id": str(snapshot.run_id),
            "line_count": line_count,
        }
    }


@router.get("/snapshots")
def get_snapshots_for_event(event_id: int, limit: int = 20, db: Session = Depends(get_db)):
    snapshots = db.execute(
        select(OddsSnapshot)
        .where(OddsSnapshot.event_id == event_id)
        .order_by(OddsSnapshot.captured_at.desc())
        .limit(limit)
    ).scalars()
    return {
        "snapshots": [
            {
                "id": snapshot.id,
                "event_id": snapshot.event_id,
                "league": snapshot.league,
                "source": snapshot.source,
                "captured_at": snapshot.captured_at,
                "run_id": str(snapshot.run_id),
            }
            for snapshot in snapshots
        ]
    }


@router.get("/lines")
def get_snapshot_lines(snapshot_id: int, limit: int = 200, offset: int = 0, db: Session = Depends(get_db)):
    lines = db.execute(select(OddsLine).where(OddsLine.snapshot_id == snapshot_id).limit(limit).offset(offset)).scalars()
    return {
        "lines": [
            {
                "id": line.id,
                "snapshot_id": line.snapshot_id,
                "event_id": line.event_id,
                "book": line.book,
                "market": line.market,
                "selection": line.selection,
                "line": line.line,
                "odds_american": line.odds_american,
                "odds_decimal": line.odds_decimal,
                "implied_prob": line.implied_prob,
            }
            for line in lines
        ]
    }
