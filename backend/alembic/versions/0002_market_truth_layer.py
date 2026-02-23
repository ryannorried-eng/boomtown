"""market truth layer schema

Revision ID: 0002_market_truth_layer
Revises: 0001_initial_foundation
Create Date: 2026-02-23 12:30:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "0002_market_truth_layer"
down_revision = "0001_initial_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("events", sa.Column("league", sa.String(length=32), nullable=False, server_default="nba"))
    op.add_column("events", sa.Column("external_id", sa.String(length=128), nullable=False, server_default=""))
    op.add_column("events", sa.Column("home_team", sa.String(length=128), nullable=True))
    op.add_column("events", sa.Column("away_team", sa.String(length=128), nullable=True))
    op.add_column("events", sa.Column("commence_time", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_events_external_id", "events", ["external_id"], unique=True)
    op.create_index("ix_events_league", "events", ["league"], unique=False)

    op.add_column("odds_snapshots", sa.Column("event_id", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("odds_snapshots", sa.Column("league", sa.String(length=32), nullable=False, server_default="nba"))
    op.add_column("odds_snapshots", sa.Column("source", sa.String(length=64), nullable=False, server_default="unknown"))
    op.add_column("odds_snapshots", sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")))
    op.add_column("odds_snapshots", sa.Column("raw_payload_hash", sa.String(length=64), nullable=False, server_default=""))
    op.add_column("odds_snapshots", sa.Column("run_id", sa.Uuid(), nullable=False, server_default="00000000-0000-0000-0000-000000000000"))
    op.create_foreign_key("fk_odds_snapshots_event_id", "odds_snapshots", "events", ["event_id"], ["id"])
    op.create_index("ix_odds_snapshots_event_id", "odds_snapshots", ["event_id"], unique=False)
    op.create_index("ix_odds_snapshots_league", "odds_snapshots", ["league"], unique=False)
    op.create_index("ix_odds_snapshots_source", "odds_snapshots", ["source"], unique=False)
    op.create_index("ix_odds_snapshots_captured_at", "odds_snapshots", ["captured_at"], unique=False)
    op.create_index("ix_odds_snapshots_raw_payload_hash", "odds_snapshots", ["raw_payload_hash"], unique=False)
    op.create_index("ix_odds_snapshots_run_id", "odds_snapshots", ["run_id"], unique=False)

    op.add_column("odds_lines", sa.Column("snapshot_id", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("odds_lines", sa.Column("event_id", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("odds_lines", sa.Column("book", sa.String(length=64), nullable=False, server_default="unknown"))
    op.add_column("odds_lines", sa.Column("market", sa.String(length=64), nullable=False, server_default="unknown"))
    op.add_column("odds_lines", sa.Column("selection", sa.String(length=128), nullable=False, server_default="unknown"))
    op.add_column("odds_lines", sa.Column("line", sa.Float(), nullable=True))
    op.add_column("odds_lines", sa.Column("odds_american", sa.Integer(), nullable=False, server_default="100"))
    op.add_column("odds_lines", sa.Column("odds_decimal", sa.Float(), nullable=False, server_default="2.0"))
    op.add_column("odds_lines", sa.Column("implied_prob", sa.Float(), nullable=False, server_default="0.5"))
    op.create_foreign_key("fk_odds_lines_snapshot_id", "odds_lines", "odds_snapshots", ["snapshot_id"], ["id"])
    op.create_foreign_key("fk_odds_lines_event_id", "odds_lines", "events", ["event_id"], ["id"])
    op.create_index("ix_odds_lines_snapshot_id", "odds_lines", ["snapshot_id"], unique=False)
    op.create_index("ix_odds_lines_event_id", "odds_lines", ["event_id"], unique=False)
    op.create_index("ix_odds_lines_book", "odds_lines", ["book"], unique=False)
    op.create_index("ix_odds_lines_market", "odds_lines", ["market"], unique=False)

    op.add_column("jobs", sa.Column("run_id", sa.Uuid(), nullable=False, server_default="00000000-0000-0000-0000-000000000000"))
    op.add_column("jobs", sa.Column("name", sa.String(length=100), nullable=False, server_default="unknown"))
    op.add_column("jobs", sa.Column("status", sa.String(length=32), nullable=False, server_default="started"))
    op.add_column("jobs", sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")))
    op.add_column("jobs", sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("jobs", sa.Column("error", sa.String(), nullable=True))
    op.add_column("jobs", sa.Column("meta", sa.JSON(), nullable=True))
    op.create_index("ix_jobs_run_id", "jobs", ["run_id"], unique=True)
    op.create_index("ix_jobs_status", "jobs", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_jobs_status", table_name="jobs")
    op.drop_index("ix_jobs_run_id", table_name="jobs")
    op.drop_column("jobs", "meta")
    op.drop_column("jobs", "error")
    op.drop_column("jobs", "ended_at")
    op.drop_column("jobs", "started_at")
    op.drop_column("jobs", "status")
    op.drop_column("jobs", "name")
    op.drop_column("jobs", "run_id")

    op.drop_index("ix_odds_lines_market", table_name="odds_lines")
    op.drop_index("ix_odds_lines_book", table_name="odds_lines")
    op.drop_index("ix_odds_lines_event_id", table_name="odds_lines")
    op.drop_index("ix_odds_lines_snapshot_id", table_name="odds_lines")
    op.drop_constraint("fk_odds_lines_event_id", "odds_lines", type_="foreignkey")
    op.drop_constraint("fk_odds_lines_snapshot_id", "odds_lines", type_="foreignkey")
    op.drop_column("odds_lines", "implied_prob")
    op.drop_column("odds_lines", "odds_decimal")
    op.drop_column("odds_lines", "odds_american")
    op.drop_column("odds_lines", "line")
    op.drop_column("odds_lines", "selection")
    op.drop_column("odds_lines", "market")
    op.drop_column("odds_lines", "book")
    op.drop_column("odds_lines", "event_id")
    op.drop_column("odds_lines", "snapshot_id")

    op.drop_index("ix_odds_snapshots_run_id", table_name="odds_snapshots")
    op.drop_index("ix_odds_snapshots_raw_payload_hash", table_name="odds_snapshots")
    op.drop_index("ix_odds_snapshots_captured_at", table_name="odds_snapshots")
    op.drop_index("ix_odds_snapshots_source", table_name="odds_snapshots")
    op.drop_index("ix_odds_snapshots_league", table_name="odds_snapshots")
    op.drop_index("ix_odds_snapshots_event_id", table_name="odds_snapshots")
    op.drop_constraint("fk_odds_snapshots_event_id", "odds_snapshots", type_="foreignkey")
    op.drop_column("odds_snapshots", "run_id")
    op.drop_column("odds_snapshots", "raw_payload_hash")
    op.drop_column("odds_snapshots", "captured_at")
    op.drop_column("odds_snapshots", "source")
    op.drop_column("odds_snapshots", "league")
    op.drop_column("odds_snapshots", "event_id")

    op.drop_index("ix_events_league", table_name="events")
    op.drop_index("ix_events_external_id", table_name="events")
    op.drop_column("events", "commence_time")
    op.drop_column("events", "away_team")
    op.drop_column("events", "home_team")
    op.drop_column("events", "external_id")
    op.drop_column("events", "league")
