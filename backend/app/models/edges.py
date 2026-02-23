from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Edge(Base, TimestampMixin):
    __tablename__ = "edges"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    # Relationship placeholders
    # picks = relationship("Pick", back_populates="edge")
