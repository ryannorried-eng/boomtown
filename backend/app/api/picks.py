from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Event, Pick
from app.services.picks_lifecycle import IMMUTABLE_PICK_FIELDS, publish_pick

router = APIRouter(tags=["picks"])


class PublishPickRequest(BaseModel):
    event_id: int
    market: str
    selection: str
    line_taken: float | None = None
    book_taken: str | None = None
    odds_taken_american: int | None = None
    pick_type: str = "consensus"
    tier: str | None = None
    model_version: str | None = None
    strategy_version: str | None = None
    run_id: UUID | None = None


@router.post("/picks/publish")
def publish(req: PublishPickRequest, db: Session = Depends(get_db)):
    event = db.execute(select(Event).where(Event.id == req.event_id)).scalar_one_or_none()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    if req.pick_type not in {"consensus", "model"}:
        raise HTTPException(status_code=400, detail="pick_type must be consensus or model")

    try:
        pick = publish_pick(
            db,
            event=event,
            market=req.market,
            selection=req.selection,
            line_taken=req.line_taken,
            book_taken=req.book_taken,
            odds_taken_american=req.odds_taken_american,
            pick_type=req.pick_type,
            tier=req.tier,
            model_version=req.model_version,
            strategy_version=req.strategy_version,
            run_id=req.run_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "pick_id": pick.pick_id,
        "published_at": pick.published_at,
        "event_id": pick.event_id,
        "league": pick.league,
        "sport": pick.sport,
        "market": pick.market,
        "selection": pick.selection,
        "line_taken": pick.line_taken,
        "odds_taken_american": pick.odds_taken_american,
        "odds_taken_decimal": pick.odds_taken_decimal,
        "book_taken": pick.book_taken,
        "implied_prob_taken": pick.implied_prob_taken,
        "snapshot_id_taken": pick.snapshot_id_taken,
        "pick_type": pick.pick_type,
        "tier": pick.tier,
        "model_version": pick.model_version,
        "strategy_version": pick.strategy_version,
        "run_id": str(pick.run_id),
    }


class PickUpdateRequest(BaseModel):
    notes: str | None = None


@router.patch("/picks/{pick_id}")
def patch_pick(pick_id: int, payload: dict, db: Session = Depends(get_db)):
    bad_fields = IMMUTABLE_PICK_FIELDS.intersection(payload.keys())
    if bad_fields:
        raise HTTPException(status_code=400, detail=f"Immutable fields cannot be updated: {sorted(bad_fields)}")

    pick = db.execute(select(Pick).where(Pick.pick_id == pick_id)).scalar_one_or_none()
    if pick is None:
        raise HTTPException(status_code=404, detail="Pick not found")

    if "notes" in payload:
        pick.notes = payload["notes"]

    db.commit()
    db.refresh(pick)
    return {"pick_id": pick.pick_id, "notes": pick.notes}


@router.get("/picks")
def list_picks(
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = select(Pick).order_by(Pick.published_at.desc()).limit(limit).offset(offset)
    if status:
        q = q.where(Pick.status == status)
    picks = db.execute(q).scalars().all()
    return {
        "items": [
            {
                "pick_id": p.pick_id,
                "published_at": p.published_at,
                "event_id": p.event_id,
                "market": p.market,
                "selection": p.selection,
                "odds_taken_american": p.odds_taken_american,
                "book_taken": p.book_taken,
                "status": p.status,
                "result": p.result,
                "clv_bps": p.clv_bps,
                "pnl_units": p.pnl_units,
            }
            for p in picks
        ]
    }
