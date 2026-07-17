"""create assistant conversation states

Revision ID: 20260717_0006
Revises: 20260717_0005
Create Date: 2026-07-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260717_0006"
down_revision = "20260717_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "assistant_conversation_states",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=True),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("whatsapp_message_id", sa.Uuid(), nullable=False),
        sa.Column("parse_result_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("pending_intent", sa.String(length=80), nullable=False),
        sa.Column("pending_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("missing_fields", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("confirmation_prompt", sa.Text(), nullable=True),
        sa.Column("last_user_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["parse_result_id"], ["assistant_parse_results.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["whatsapp_message_id"], ["whatsapp_messages.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("assistant_conversation_states")
