from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class OddsSnapshot(Base, TimestampMixin):
    __tablename__ = "odds_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    # Relationship placeholders
    # odds_lines = relationship("OddsLine", back_populates="snapshot")
