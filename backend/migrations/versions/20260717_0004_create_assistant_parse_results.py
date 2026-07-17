"""create assistant parse results

Revision ID: 20260717_0004
Revises: 20260717_0003
Create Date: 2026-07-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260717_0004"
down_revision = "20260717_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "assistant_parse_results",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=True),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("whatsapp_message_id", sa.Uuid(), nullable=False),
        sa.Column("intent", sa.String(length=80), nullable=False),
        sa.Column("confidence", sa.String(length=40), nullable=False),
        sa.Column("input_language", sa.String(length=40), nullable=True),
        sa.Column("extracted_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("missing_fields", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("validation_status", sa.String(length=50), nullable=False),
        sa.Column("assistant_summary", sa.Text(), nullable=True),
        sa.Column("next_action", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["whatsapp_message_id"], ["whatsapp_messages.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("assistant_parse_results")
