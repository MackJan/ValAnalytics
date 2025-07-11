"""Fix composite primary key on ActiveMatchPlayer

Revision ID: aaa_fix_composite_key
Revises: 966d8c041ff1
Create Date: 2025-07-12 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = 'aaa_fix_composite_key'
down_revision: Union[str, None] = '966d8c041ff1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('activematchplayer') as batch_op:
        batch_op.drop_constraint('activematchplayer_pkey', type_='primary')
        batch_op.create_primary_key('activematchplayer_pkey', ['subject', 'match_id'])


def downgrade() -> None:
    with op.batch_alter_table('activematchplayer') as batch_op:
        batch_op.drop_constraint('activematchplayer_pkey', type_='primary')
        batch_op.create_primary_key('activematchplayer_pkey', ['subject'])
