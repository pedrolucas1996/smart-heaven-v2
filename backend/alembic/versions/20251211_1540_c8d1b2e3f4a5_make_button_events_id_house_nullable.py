"""make button_events id_house nullable

Revision ID: c8d1b2e3f4a5
Revises: b9720db985f1
Create Date: 2025-12-11 15:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'c8d1b2e3f4a5'
down_revision: Union[str, None] = 'b9720db985f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make id_house nullable in button_events table
    # Also set default value to 1 for existing rows
    op.execute('ALTER TABLE button_events MODIFY id_house INT NULL DEFAULT 1')


def downgrade() -> None:
    # Revert id_house to NOT NULL in button_events table
    op.execute('UPDATE button_events SET id_house = 1 WHERE id_house IS NULL')
    op.execute('ALTER TABLE button_events MODIFY id_house INT NOT NULL')
