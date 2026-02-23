from __future__ import annotations

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class OddsLine(Base, TimestampMixin):
    __tablename__ = "odds_lines"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    snapshot_id: Mapped[int] = mapped_column(ForeignKey("odds_snapshots.id"), nullable=False, index=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False, index=True)
    book: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    market: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    selection: Mapped[str] = mapped_column(String(128), nullable=False)
    line: Mapped[float | None] = mapped_column(Float, nullable=True)
    odds_american: Mapped[int] = mapped_column(Integer, nullable=False)
    odds_decimal: Mapped[float] = mapped_column(Float, nullable=False)
    implied_prob: Mapped[float] = mapped_column(Float, nullable=False)
