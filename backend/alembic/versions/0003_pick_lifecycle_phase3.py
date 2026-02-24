"""pick lifecycle and clv plumbing

Revision ID: 0003_pick_lifecycle_phase3
Revises: 0002_market_truth_layer
Create Date: 2026-02-23 13:30:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "0003_pick_lifecycle_phase3"
down_revision = "0002_market_truth_layer"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_picks_id", table_name="picks")
    op.alter_column("picks", "id", new_column_name="pick_id")
    op.create_index("ix_picks_pick_id", "picks", ["pick_id"], unique=False)

    op.add_column("picks", sa.Column("published_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")))
    op.add_column("picks", sa.Column("event_id", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("picks", sa.Column("league", sa.String(length=32), nullable=False, server_default="nba"))
    op.add_column("picks", sa.Column("sport", sa.String(length=32), nullable=False, server_default="basketball_nba"))
    op.add_column("picks", sa.Column("market", sa.String(length=64), nullable=False, server_default="h2h"))
    op.add_column("picks", sa.Column("selection", sa.String(length=128), nullable=False, server_default="home"))
    op.add_column("picks", sa.Column("line_taken", sa.Float(), nullable=True))
    op.add_column("picks", sa.Column("odds_taken_american", sa.Integer(), nullable=False, server_default="-110"))
    op.add_column("picks", sa.Column("odds_taken_decimal", sa.Float(), nullable=False, server_default="1.91"))
    op.add_column("picks", sa.Column("book_taken", sa.String(length=64), nullable=False, server_default="manual"))
    op.add_column("picks", sa.Column("implied_prob_taken", sa.Float(), nullable=False, server_default="0.5238"))
    op.add_column("picks", sa.Column("snapshot_id_taken", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("picks", sa.Column("pick_type", sa.String(length=32), nullable=False, server_default="consensus"))
    op.add_column("picks", sa.Column("tier", sa.String(length=32), nullable=True))
    op.add_column("picks", sa.Column("model_version", sa.String(length=64), nullable=True))
    op.add_column("picks", sa.Column("strategy_version", sa.String(length=64), nullable=True))
    op.add_column("picks", sa.Column("run_id", sa.Uuid(), nullable=False, server_default="00000000-0000-0000-0000-000000000000"))

    op.add_column("picks", sa.Column("close_captured_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("picks", sa.Column("close_snapshot_id", sa.Integer(), nullable=True))
    op.add_column("picks", sa.Column("close_book", sa.String(length=64), nullable=True))
    op.add_column("picks", sa.Column("close_odds_american", sa.Integer(), nullable=True))
    op.add_column("picks", sa.Column("close_odds_decimal", sa.Float(), nullable=True))
    op.add_column("picks", sa.Column("implied_prob_close", sa.Float(), nullable=True))
    op.add_column("picks", sa.Column("clv_bps", sa.Float(), nullable=True))

    op.add_column("picks", sa.Column("status", sa.String(length=16), nullable=False, server_default="open"))
    op.add_column("picks", sa.Column("result", sa.String(length=16), nullable=True))
    op.add_column("picks", sa.Column("settled_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("picks", sa.Column("pnl_units", sa.Float(), nullable=True))
    op.add_column("picks", sa.Column("notes", sa.String(), nullable=True))

    op.create_foreign_key("fk_picks_event_id", "picks", "events", ["event_id"], ["id"])
    op.create_foreign_key("fk_picks_snapshot_id_taken", "picks", "odds_snapshots", ["snapshot_id_taken"], ["id"])
    op.create_foreign_key("fk_picks_close_snapshot_id", "picks", "odds_snapshots", ["close_snapshot_id"], ["id"])
    op.create_index("ix_picks_event_id", "picks", ["event_id"], unique=False)
    op.create_index("ix_picks_published_at", "picks", ["published_at"], unique=False)
    op.create_index("ix_picks_status", "picks", ["status"], unique=False)
    op.create_index("ix_picks_snapshot_id_taken", "picks", ["snapshot_id_taken"], unique=False)
    op.create_index("ix_picks_close_snapshot_id", "picks", ["close_snapshot_id"], unique=False)

    op.add_column("events", sa.Column("is_completed", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("events", sa.Column("result", sa.String(length=16), nullable=True))
    op.add_column("events", sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_events_is_completed", "events", ["is_completed"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_events_is_completed", table_name="events")
    op.drop_column("events", "completed_at")
    op.drop_column("events", "result")
    op.drop_column("events", "is_completed")

    op.drop_index("ix_picks_close_snapshot_id", table_name="picks")
    op.drop_index("ix_picks_snapshot_id_taken", table_name="picks")
    op.drop_index("ix_picks_status", table_name="picks")
    op.drop_index("ix_picks_published_at", table_name="picks")
    op.drop_index("ix_picks_event_id", table_name="picks")
    op.drop_constraint("fk_picks_close_snapshot_id", "picks", type_="foreignkey")
    op.drop_constraint("fk_picks_snapshot_id_taken", "picks", type_="foreignkey")
    op.drop_constraint("fk_picks_event_id", "picks", type_="foreignkey")

    for col in [
        "notes",
        "pnl_units",
        "settled_at",
        "result",
        "status",
        "clv_bps",
        "implied_prob_close",
        "close_odds_decimal",
        "close_odds_american",
        "close_book",
        "close_snapshot_id",
        "close_captured_at",
        "run_id",
        "strategy_version",
        "model_version",
        "tier",
        "pick_type",
        "snapshot_id_taken",
        "implied_prob_taken",
        "book_taken",
        "odds_taken_decimal",
        "odds_taken_american",
        "line_taken",
        "selection",
        "market",
        "sport",
        "league",
        "event_id",
        "published_at",
    ]:
        op.drop_column("picks", col)

    op.drop_index("ix_picks_pick_id", table_name="picks")
    op.alter_column("picks", "pick_id", new_column_name="id")
    op.create_index("ix_picks_id", "picks", ["id"], unique=False)
