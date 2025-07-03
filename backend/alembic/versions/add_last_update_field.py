"""add last_update to ActiveMatches

Revision ID: add_last_update_field
Revises: 849e4152c797
Create Date: 2025-06-28 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'add_last_update_field'
down_revision = '849e4152c797'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add the last_update column to ActiveMatches table
    op.add_column('activematches', sa.Column('last_update', sa.DateTime(), nullable=False, default=datetime.now))

    # Update existing records to have the current timestamp
    op.execute("UPDATE activematches SET last_update = started_at WHERE last_update IS NULL")


def downgrade() -> None:
    # Remove the last_update column
    op.drop_column('activematches', 'last_update')
