# boomtown (foundation phase)

Autonomous paper-trading sports betting analytics platform skeleton focused on proving predictive edge via CLV.

## What this phase includes
- Runnable FastAPI backend with lifecycle hooks.
- PostgreSQL connectivity and SQLAlchemy foundation.
- Alembic baseline migration for core tables.
- Service contracts (interfaces only).
- Placeholder utility modules for odds/EV/CLV.
- Docker Compose orchestration for backend + postgres.
- Frontend React placeholder.

## Quick start
```bash
docker compose up --build
```

Backend health endpoint:
- `http://localhost:8000/health`

## Alembic migrations
Migrations are executed automatically when the backend container starts:
- `alembic -c alembic.ini upgrade head`

Manual run (inside `backend/`):
```bash
alembic -c alembic.ini upgrade head
```

## Local backend development
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Run tests
```bash
cd backend
pytest
```

## Intentionally unimplemented (by design in foundation phase)
- Any domain/business logic for odds ingestion, feature engineering, modeling, recommendations, settlement, or CLV computation.
- Any mutation/publishing workflow for picks.
- Any sports-specific schema fields.
- Frontend UI implementation beyond placeholder metadata.

All utility calculation functions currently raise `NotImplementedError` and all service contracts are abstract signatures only.
