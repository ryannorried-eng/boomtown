from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Book(Base, TimestampMixin):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    # Relationship placeholders
    # odds_snapshots = relationship("OddsSnapshot", back_populates="book")
