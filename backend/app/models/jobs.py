from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Job(Base, TimestampMixin):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    # Relationship placeholders
    # Add scheduler and processing relationships in future phases.
