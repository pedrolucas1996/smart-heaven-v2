"""Add button_events table

Revision ID: d15eff8184a8
Revises: 584cac1f73e2
Create Date: 2025-12-09 08:18:35.384454

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'd15eff8184a8'
down_revision: Union[str, None] = '584cac1f73e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create button_events table for logging button/switch press events
    op.create_table('button_events',
        sa.Column('id', mysql.BIGINT(unsigned=True), autoincrement=True, nullable=False),
        sa.Column('device', mysql.VARCHAR(length=50), nullable=False, comment='Device identifier (e.g., Base_D, Base_A)'),
        sa.Column('button', mysql.VARCHAR(length=50), nullable=False, comment='Button identifier (e.g., S1, B2)'),
        sa.Column('action', mysql.VARCHAR(length=20), nullable=False, comment='Action: press, release, changed'),
        sa.Column('origin', mysql.VARCHAR(length=50), nullable=True, comment='Event origin (mqtt, api, etc)'),
        sa.Column('rssi', mysql.INTEGER(), nullable=True, comment='WiFi signal strength (optional)'),
        sa.Column('data_hora', sa.DateTime(), nullable=False, server_default=sa.func.now(), comment='When event occurred'),
        sa.PrimaryKeyConstraint('id'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_general_ci',
        mysql_engine='InnoDB'
    )
    op.create_index('ix_button_events_device', 'button_events', ['device'], unique=False)
    op.create_index('ix_button_events_data_hora', 'button_events', ['data_hora'], unique=False)
    op.create_index('ix_button_events_button', 'button_events', ['button'], unique=False)
    op.create_index('idx_device_hora', 'button_events', ['device', 'data_hora'], unique=False)
    op.create_index('idx_device_button_hora', 'button_events', ['device', 'button', 'data_hora'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_device_button_hora', table_name='button_events')
    op.drop_index('idx_device_hora', table_name='button_events')
    op.drop_index('ix_button_events_button', table_name='button_events')
    op.drop_index('ix_button_events_data_hora', table_name='button_events')
    op.drop_index('ix_button_events_device', table_name='button_events')
    op.drop_table('button_events')
