from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Event(Base, TimestampMixin):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    # Relationship placeholders
    # odds_snapshots = relationship("OddsSnapshot", back_populates="event")
    # model_predictions = relationship("ModelPrediction", back_populates="event")
