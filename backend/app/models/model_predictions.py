from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class ModelPrediction(Base, TimestampMixin):
    __tablename__ = "model_predictions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    # Relationship placeholders
    # edges = relationship("Edge", back_populates="model_prediction")
