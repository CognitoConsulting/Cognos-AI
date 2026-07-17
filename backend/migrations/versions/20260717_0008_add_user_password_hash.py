"""add user password hash

Revision ID: 20260717_0008
Revises: 20260717_0007
Create Date: 2026-07-17

"""
from alembic import op
import sqlalchemy as sa


revision = "20260717_0008"
down_revision = "20260717_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("password_hash", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "password_hash")
