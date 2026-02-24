from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Pick(Base, TimestampMixin):
    __tablename__ = "picks"

    pick_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False, index=True)
    league: Mapped[str] = mapped_column(String(32), nullable=False)
    sport: Mapped[str] = mapped_column(String(32), nullable=False, default="basketball_nba", server_default="basketball_nba")
    market: Mapped[str] = mapped_column(String(64), nullable=False)
    selection: Mapped[str] = mapped_column(String(128), nullable=False)
    line_taken: Mapped[float | None] = mapped_column(Float, nullable=True)
    odds_taken_american: Mapped[int] = mapped_column(Integer, nullable=False)
    odds_taken_decimal: Mapped[float] = mapped_column(Float, nullable=False)
    book_taken: Mapped[str] = mapped_column(String(64), nullable=False)
    implied_prob_taken: Mapped[float] = mapped_column(Float, nullable=False)
    snapshot_id_taken: Mapped[int] = mapped_column(ForeignKey("odds_snapshots.id"), nullable=False, index=True)
    pick_type: Mapped[str] = mapped_column(String(32), nullable=False)
    tier: Mapped[str | None] = mapped_column(String(32), nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    strategy_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    run_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)

    close_captured_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    close_snapshot_id: Mapped[int | None] = mapped_column(ForeignKey("odds_snapshots.id"), nullable=True, index=True)
    close_book: Mapped[str | None] = mapped_column(String(64), nullable=True)
    close_odds_american: Mapped[int | None] = mapped_column(Integer, nullable=True)
    close_odds_decimal: Mapped[float | None] = mapped_column(Float, nullable=True)
    implied_prob_close: Mapped[float | None] = mapped_column(Float, nullable=True)
    clv_bps: Mapped[float | None] = mapped_column(Float, nullable=True)

    status: Mapped[str] = mapped_column(String(16), nullable=False, default="open", server_default="open", index=True)
    result: Mapped[str | None] = mapped_column(String(16), nullable=True)
    settled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    pnl_units: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
