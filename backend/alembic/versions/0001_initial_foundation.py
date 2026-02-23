"""initial foundation schema

Revision ID: 0001_initial_foundation
Revises:
Create Date: 2026-02-23 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_foundation"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    table_names = [
        "events",
        "books",
        "odds_snapshots",
        "odds_lines",
        "model_predictions",
        "edges",
        "picks",
        "jobs",
    ]

    for table_name in table_names:
        op.create_table(
            table_name,
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f(f"ix_{table_name}_id"), table_name, ["id"], unique=False)


def downgrade() -> None:
    table_names = [
        "jobs",
        "picks",
        "edges",
        "model_predictions",
        "odds_lines",
        "odds_snapshots",
        "books",
        "events",
    ]
    for table_name in table_names:
        op.drop_index(op.f(f"ix_{table_name}_id"), table_name=table_name)
        op.drop_table(table_name)
