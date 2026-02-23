from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class OddsLine(Base, TimestampMixin):
    __tablename__ = "odds_lines"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    # Relationship placeholders
    # snapshot = relationship("OddsSnapshot", back_populates="odds_lines")
