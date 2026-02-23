from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.jobs.runner import run_job_once
from app.services.odds_collector import NbaOddsCollector

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/poll_odds")
def poll_odds_once(league: str = Query("nba"), db: Session = Depends(get_db)):
    if league.lower() != "nba":
        raise HTTPException(status_code=400, detail="Only nba league is supported")

    collector = NbaOddsCollector(db=db)
    job = run_job_once(db, name="poll_odds", fn=lambda run_id: collector.collect_and_store(league=league, run_id=run_id))

    return {
        "job": {
            "id": job.id,
            "run_id": str(job.run_id),
            "name": job.name,
            "status": job.status,
            "started_at": job.started_at,
            "ended_at": job.ended_at,
            "error": job.error,
            "meta": job.meta,
        }
    }
