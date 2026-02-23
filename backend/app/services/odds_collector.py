from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Event, OddsLine, OddsSnapshot
from app.services.contracts import OddsCollector
from app.utils.odds_math import american_to_decimal, american_to_probability


class NbaOddsCollector(OddsCollector):
    def __init__(self, db: Session):
        self.db = db

    def collect(self) -> list[dict[str, Any]]:
        url = f"{settings.odds_api_base_url}/sports/basketball_nba/odds"
        response = httpx.get(
            url,
            params={"apiKey": settings.odds_api_key, "oddsFormat": "american", "dateFormat": "iso"},
            timeout=20.0,
        )
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, list) else []

    def collect_and_store(self, league: str, run_id) -> dict[str, int]:
        if league.lower() != "nba":
            raise ValueError("Only nba league is supported")

        events_payload = self.collect()
        source = settings.odds_source_name
        snapshots_inserted = 0
        lines_inserted = 0

        for event_payload in events_payload:
            event = self._upsert_event(event_payload)
            raw_hash = hashlib.sha256(json.dumps(event_payload, sort_keys=True).encode("utf-8")).hexdigest()

            existing_snapshot = self.db.execute(
                select(OddsSnapshot).where(
                    OddsSnapshot.source == source,
                    OddsSnapshot.raw_payload_hash == raw_hash,
                )
            ).scalar_one_or_none()

            if existing_snapshot is not None:
                continue

            snapshot = OddsSnapshot(
                event_id=event.id,
                league=league,
                source=source,
                captured_at=datetime.utcnow(),
                raw_payload_hash=raw_hash,
                run_id=run_id,
            )
            self.db.add(snapshot)
            self.db.flush()
            snapshots_inserted += 1

            for book in event_payload.get("bookmakers", []):
                book_name = book.get("key") or book.get("title") or "unknown"
                for market in book.get("markets", []):
                    market_key = market.get("key", "unknown")
                    for outcome in market.get("outcomes", []):
                        american_odds = int(outcome["price"])
                        self.db.add(
                            OddsLine(
                                snapshot_id=snapshot.id,
                                event_id=event.id,
                                book=book_name,
                                market=market_key,
                                selection=str(outcome.get("name", "unknown")),
                                line=outcome.get("point"),
                                odds_american=american_odds,
                                odds_decimal=american_to_decimal(american_odds),
                                implied_prob=american_to_probability(american_odds),
                            )
                        )
                        lines_inserted += 1

        self.db.commit()
        return {"snapshots": snapshots_inserted, "lines": lines_inserted}

    def _upsert_event(self, event_payload: dict[str, Any]) -> Event:
        external_id = str(event_payload.get("id"))
        event = self.db.execute(select(Event).where(Event.external_id == external_id)).scalar_one_or_none()
        commence_raw = event_payload.get("commence_time")
        commence_time = datetime.fromisoformat(commence_raw.replace("Z", "+00:00")) if commence_raw else None

        if event is None:
            event = Event(
                league="nba",
                external_id=external_id,
                home_team=event_payload.get("home_team"),
                away_team=event_payload.get("away_team"),
                commence_time=commence_time,
            )
            self.db.add(event)
            self.db.flush()
            return event

        event.home_team = event_payload.get("home_team")
        event.away_team = event_payload.get("away_team")
        event.commence_time = commence_time
        self.db.flush()
        return event
