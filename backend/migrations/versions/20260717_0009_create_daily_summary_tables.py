"""create daily summary tables

Revision ID: 20260717_0009
Revises: 20260717_0008
Create Date: 2026-07-17

"""
from alembic import op
import sqlalchemy as sa


revision = "20260717_0009"
down_revision = "20260717_0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "daily_summary_settings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("send_time_local", sa.Time(), nullable=False),
        sa.Column("timezone", sa.String(length=80), nullable=False),
        sa.Column("recipient_scope", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", name="uq_daily_summary_settings_project"),
    )

    op.create_table(
        "daily_summary_messages",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("summary_date", sa.Date(), nullable=False),
        sa.Column("summary_text", sa.Text(), nullable=False),
        sa.Column("recipient_user_id", sa.Uuid(), nullable=True),
        sa.Column("recipient_phone", sa.String(length=40), nullable=True),
        sa.Column("whatsapp_message_id", sa.Uuid(), nullable=True),
        sa.Column("delivery_status", sa.String(length=50), nullable=False),
        sa.Column("trigger_type", sa.String(length=80), nullable=False),
        sa.Column("triggered_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["recipient_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["triggered_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["whatsapp_message_id"], ["whatsapp_messages.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_daily_summary_messages_project_date",
        "daily_summary_messages",
        ["project_id", "summary_date"],
    )


def downgrade() -> None:
    op.drop_index("ix_daily_summary_messages_project_date", table_name="daily_summary_messages")
    op.drop_table("daily_summary_messages")
    op.drop_table("daily_summary_settings")
