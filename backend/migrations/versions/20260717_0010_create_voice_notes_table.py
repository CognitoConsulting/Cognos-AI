"""create voice notes table

Revision ID: 20260717_0010
Revises: 20260717_0009
Create Date: 2026-07-17

"""
from alembic import op
import sqlalchemy as sa


revision = "20260717_0010"
down_revision = "20260717_0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "voice_notes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=True),
        sa.Column("uploaded_by", sa.Uuid(), nullable=True),
        sa.Column("source_whatsapp_message_id", sa.Uuid(), nullable=True),
        sa.Column("storage_url", sa.String(length=500), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=True),
        sa.Column("provider_media_id", sa.String(length=255), nullable=True),
        sa.Column("mime_type", sa.String(length=120), nullable=True),
        sa.Column("transcription_status", sa.String(length=50), nullable=False),
        sa.Column("transcription_provider", sa.String(length=120), nullable=True),
        sa.Column("transcript_text", sa.Text(), nullable=True),
        sa.Column("transcript_language", sa.String(length=50), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["source_whatsapp_message_id"], ["whatsapp_messages.id"]),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_voice_notes_company_created", "voice_notes", ["company_id", "created_at"])
    op.create_index("ix_voice_notes_project_created", "voice_notes", ["project_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_voice_notes_project_created", table_name="voice_notes")
    op.drop_index("ix_voice_notes_company_created", table_name="voice_notes")
    op.drop_table("voice_notes")
