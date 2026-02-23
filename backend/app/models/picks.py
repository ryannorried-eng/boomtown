from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Pick(Base, TimestampMixin):
    __tablename__ = "picks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    # Relationship placeholders
    # edge = relationship("Edge", back_populates="picks")
