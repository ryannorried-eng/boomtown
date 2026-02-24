from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.picks_lifecycle import clv_distribution, metrics_summary

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    return metrics_summary(db)


@router.get("/clv_distribution")
def distribution(bins: int = Query(20, ge=1, le=200), db: Session = Depends(get_db)):
    return clv_distribution(db, bins)
