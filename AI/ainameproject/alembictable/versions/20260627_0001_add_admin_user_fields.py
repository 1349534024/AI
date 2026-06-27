"""add admin user fields

Revision ID: 20260627_0001
Revises: 20260626_add_user_role
Create Date: 2026-06-27 00:01:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "20260627_0001"
down_revision = "20260626_add_user_role"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user", sa.Column("is_admin", sa.Boolean(), server_default="0", nullable=False))
    op.add_column("user", sa.Column("is_active", sa.Boolean(), server_default="1", nullable=False))


def downgrade() -> None:
    op.drop_column("user", "is_active")
    op.drop_column("user", "is_admin")
