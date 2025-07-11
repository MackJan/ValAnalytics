"""Merge ActiveMatch and ActiveMatchPlayer migrations

Revision ID: 966d8c041ff1
Revises: add_last_update_field
Create Date: 2025-07-11 08:41:47.745137

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '966d8c041ff1'
down_revision: Union[str, None] = 'add_last_update_field'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create activematch table with all final columns
    op.create_table('activematch',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('match_uuid', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column('game_map', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
                    sa.Column('game_start', sa.DateTime(), nullable=True),
                    sa.Column('game_mode', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
                    sa.Column('state', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
                    sa.Column('party_owner_score', sa.Integer(), nullable=True),
                    sa.Column('party_owner_enemy_score', sa.Integer(), nullable=True),
                    sa.Column('party_size', sa.Integer(), nullable=True),
                    sa.Column('last_updated', sa.DateTime(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('ended_at', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_activematch_match_uuid'), 'activematch', ['match_uuid'], unique=True)

    # Create activematchplayer table with all final columns
    op.create_table('activematchplayer',
                    sa.Column('subject', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column('character', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column('team_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column('game_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column('account_level', sa.Integer(), nullable=True),
                    sa.Column('player_card_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
                    sa.Column('player_title_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
                    sa.Column('preferred_level_border_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
                    sa.Column('agent_icon', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column('rank', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column('rr', sa.Integer(), nullable=True),
                    sa.Column('leaderboard_rank', sa.Integer(), nullable=True),
                    sa.Column('match_id', sa.Integer(), nullable=False),
                    sa.PrimaryKeyConstraint('subject')
                    )
    op.create_index(op.f('ix_activematchplayer_subject'), 'activematchplayer', ['subject'], unique=False)
    op.create_index(op.f('ix_activematchplayer_match_id'), 'activematchplayer', ['match_id'], unique=False)
    op.create_foreign_key(None, 'activematchplayer', 'activematch', ['match_id'], ['id'])

    # Drop old activematches table if it exists
    op.drop_index(op.f('ix_activematches_match_uuid'), table_name='activematches')
    op.drop_table('activematches')


def downgrade() -> None:
    """Downgrade schema."""
    # Recreate old activematches table
    op.create_table('activematches',
                    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                    sa.Column('match_uuid', sa.VARCHAR(), autoincrement=False, nullable=False),
                    sa.Column('started_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
                    sa.Column('ended_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('last_update', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
                    sa.PrimaryKeyConstraint('id', name=op.f('activematches_pkey'))
                    )
    op.create_index(op.f('ix_activematches_match_uuid'), 'activematches', ['match_uuid'], unique=True)

    # Drop new tables
    op.drop_constraint(None, 'activematchplayer', type_='foreignkey')
    op.drop_index(op.f('ix_activematchplayer_match_id'), table_name='activematchplayer')
    op.drop_index(op.f('ix_activematchplayer_subject'), table_name='activematchplayer')
    op.drop_table('activematchplayer')
    op.drop_index(op.f('ix_activematch_match_uuid'), table_name='activematch')
    op.drop_table('activematch')
