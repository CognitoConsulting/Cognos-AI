"""create whatsapp provider tables

Revision ID: 20260717_0003
Revises: 20260717_0002
Create Date: 2026-07-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260717_0003"
down_revision = "20260717_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "whatsapp_provider_accounts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("provider_name", sa.String(length=80), nullable=False),
        sa.Column("provider_account_id", sa.String(length=255), nullable=True),
        sa.Column("webhook_url", sa.String(length=500), nullable=True),
        sa.Column("phone_number_id", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "company_id",
            "provider_name",
            "phone_number_id",
            name="uq_whatsapp_provider_accounts_company_provider_phone",
        ),
    )

    op.create_table(
        "whatsapp_messages",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=True),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("phone", sa.String(length=40), nullable=True),
        sa.Column("direction", sa.String(length=20), nullable=False),
        sa.Column("message_text", sa.Text(), nullable=True),
        sa.Column("provider_name", sa.String(length=80), nullable=False),
        sa.Column("provider_message_id", sa.String(length=255), nullable=True),
        sa.Column("provider_account_id", sa.String(length=255), nullable=True),
        sa.Column("raw_provider_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("processing_status", sa.String(length=50), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "provider_name",
            "provider_message_id",
            name="uq_whatsapp_messages_provider_message_id",
        ),
    )


def downgrade() -> None:
    op.drop_table("whatsapp_messages")
    op.drop_table("whatsapp_provider_accounts")
