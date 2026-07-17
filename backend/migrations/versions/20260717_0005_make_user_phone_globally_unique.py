"""make user phone globally unique

Revision ID: 20260717_0005
Revises: 20260717_0004
Create Date: 2026-07-17

"""
from alembic import op


revision = "20260717_0005"
down_revision = "20260717_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint("uq_users_phone", "users", ["phone"])


def downgrade() -> None:
    op.drop_constraint("uq_users_phone", "users", type_="unique")
