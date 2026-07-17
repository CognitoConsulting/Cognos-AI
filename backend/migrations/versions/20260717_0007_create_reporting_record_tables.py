"""create reporting record tables

Revision ID: 20260717_0007
Revises: 20260717_0006
Create Date: 2026-07-17

"""
from alembic import op
import sqlalchemy as sa


revision = "20260717_0007"
down_revision = "20260717_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "progress_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("entered_by", sa.Uuid(), nullable=True),
        sa.Column("source_whatsapp_message_id", sa.Uuid(), nullable=True),
        sa.Column("assistant_conversation_state_id", sa.Uuid(), nullable=True),
        sa.Column("activity_id", sa.Uuid(), nullable=True),
        sa.Column("activity_name", sa.String(length=255), nullable=False),
        sa.Column("area_id", sa.Uuid(), nullable=True),
        sa.Column("sub_area_id", sa.Uuid(), nullable=True),
        sa.Column("location_text", sa.String(length=255), nullable=True),
        sa.Column("quantity", sa.Numeric(14, 3), nullable=False),
        sa.Column("unit_id", sa.Uuid(), nullable=True),
        sa.Column("unit_symbol", sa.String(length=40), nullable=True),
        sa.Column("work_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("original_text", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["activity_id"], ["activities.id"]),
        sa.ForeignKeyConstraint(["area_id"], ["project_locations.id"]),
        sa.ForeignKeyConstraint(["assistant_conversation_state_id"], ["assistant_conversation_states.id"]),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["entered_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["source_whatsapp_message_id"], ["whatsapp_messages.id"]),
        sa.ForeignKeyConstraint(["sub_area_id"], ["project_locations.id"]),
        sa.ForeignKeyConstraint(["unit_id"], ["units.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_progress_entries_project_date", "progress_entries", ["project_id", "work_date"])

    op.create_table(
        "manpower_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("entered_by", sa.Uuid(), nullable=True),
        sa.Column("source_whatsapp_message_id", sa.Uuid(), nullable=True),
        sa.Column("assistant_conversation_state_id", sa.Uuid(), nullable=True),
        sa.Column("trade_name", sa.String(length=120), nullable=False),
        sa.Column("worker_count", sa.Integer(), nullable=False),
        sa.Column("area_id", sa.Uuid(), nullable=True),
        sa.Column("sub_area_id", sa.Uuid(), nullable=True),
        sa.Column("location_text", sa.String(length=255), nullable=True),
        sa.Column("work_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("original_text", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["area_id"], ["project_locations.id"]),
        sa.ForeignKeyConstraint(["assistant_conversation_state_id"], ["assistant_conversation_states.id"]),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["entered_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["source_whatsapp_message_id"], ["whatsapp_messages.id"]),
        sa.ForeignKeyConstraint(["sub_area_id"], ["project_locations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_manpower_entries_project_date", "manpower_entries", ["project_id", "work_date"])

    op.create_table(
        "material_transactions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("entered_by", sa.Uuid(), nullable=True),
        sa.Column("source_whatsapp_message_id", sa.Uuid(), nullable=True),
        sa.Column("assistant_conversation_state_id", sa.Uuid(), nullable=True),
        sa.Column("transaction_type", sa.String(length=40), nullable=False),
        sa.Column("material_name", sa.String(length=255), nullable=False),
        sa.Column("boq_item_id", sa.Uuid(), nullable=True),
        sa.Column("quantity", sa.Numeric(14, 3), nullable=False),
        sa.Column("unit_id", sa.Uuid(), nullable=True),
        sa.Column("unit_symbol", sa.String(length=40), nullable=True),
        sa.Column("supplier_name", sa.String(length=255), nullable=True),
        sa.Column("issued_to", sa.String(length=255), nullable=True),
        sa.Column("purpose", sa.String(length=255), nullable=True),
        sa.Column("area_id", sa.Uuid(), nullable=True),
        sa.Column("sub_area_id", sa.Uuid(), nullable=True),
        sa.Column("location_text", sa.String(length=255), nullable=True),
        sa.Column("transaction_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("proof_status", sa.String(length=50), nullable=False),
        sa.Column("original_text", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["area_id"], ["project_locations.id"]),
        sa.ForeignKeyConstraint(["assistant_conversation_state_id"], ["assistant_conversation_states.id"]),
        sa.ForeignKeyConstraint(["boq_item_id"], ["boq_items.id"]),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["entered_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["source_whatsapp_message_id"], ["whatsapp_messages.id"]),
        sa.ForeignKeyConstraint(["sub_area_id"], ["project_locations.id"]),
        sa.ForeignKeyConstraint(["unit_id"], ["units.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_material_transactions_project_date",
        "material_transactions",
        ["project_id", "transaction_date"],
    )

    op.create_table(
        "material_stock_balances",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("material_name", sa.String(length=255), nullable=False),
        sa.Column("boq_item_id", sa.Uuid(), nullable=True),
        sa.Column("unit_id", sa.Uuid(), nullable=True),
        sa.Column("unit_symbol", sa.String(length=40), nullable=False),
        sa.Column("total_received", sa.Numeric(14, 3), nullable=False),
        sa.Column("total_issued", sa.Numeric(14, 3), nullable=False),
        sa.Column("current_balance", sa.Numeric(14, 3), nullable=False),
        sa.Column("low_stock_threshold", sa.Numeric(14, 3), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["boq_item_id"], ["boq_items.id"]),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["unit_id"], ["units.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "project_id",
            "material_name",
            "unit_symbol",
            name="uq_material_stock_project_material_unit",
        ),
    )

    op.create_table(
        "media_files",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("uploaded_by", sa.Uuid(), nullable=True),
        sa.Column("source_whatsapp_message_id", sa.Uuid(), nullable=True),
        sa.Column("linked_entity_type", sa.String(length=80), nullable=True),
        sa.Column("linked_entity_id", sa.Uuid(), nullable=True),
        sa.Column("media_type", sa.String(length=50), nullable=False),
        sa.Column("storage_url", sa.String(length=500), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=True),
        sa.Column("caption", sa.Text(), nullable=True),
        sa.Column("provider_media_id", sa.String(length=255), nullable=True),
        sa.Column("processing_status", sa.String(length=50), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["source_whatsapp_message_id"], ["whatsapp_messages.id"]),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_media_files_project_created", "media_files", ["project_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_media_files_project_created", table_name="media_files")
    op.drop_table("media_files")
    op.drop_table("material_stock_balances")
    op.drop_index("ix_material_transactions_project_date", table_name="material_transactions")
    op.drop_table("material_transactions")
    op.drop_index("ix_manpower_entries_project_date", table_name="manpower_entries")
    op.drop_table("manpower_entries")
    op.drop_index("ix_progress_entries_project_date", table_name="progress_entries")
    op.drop_table("progress_entries")
