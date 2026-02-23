from __future__ import annotations

import traceback
from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models import Job


def run_job_once(db: Session, name: str, fn):
    run_id = uuid4()
    job = Job(run_id=run_id, name=name, status="started", started_at=datetime.utcnow(), meta={})
    db.add(job)
    db.commit()
    db.refresh(job)

    try:
        result = fn(run_id)
        job.status = "succeeded"
        job.ended_at = datetime.utcnow()
        job.meta = result if isinstance(result, dict) else {"result": result}
        db.add(job)
        db.commit()
        db.refresh(job)
        return job
    except Exception as exc:
        job.status = "failed"
        job.ended_at = datetime.utcnow()
        job.error = str(exc)
        job.meta = {"traceback": traceback.format_exc()}
        db.add(job)
        db.commit()
        db.refresh(job)
        return job
