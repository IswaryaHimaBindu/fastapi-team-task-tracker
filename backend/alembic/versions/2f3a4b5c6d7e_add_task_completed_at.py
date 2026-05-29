"""Add completed_at to tasks

Revision ID: 2f3a4b5c6d7e
Revises: 9b881035083e
Create Date: 2026-05-29 17:10:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2f3a4b5c6d7e'
down_revision = '9b881035083e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('tasks', sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('tasks', 'completed_at')
