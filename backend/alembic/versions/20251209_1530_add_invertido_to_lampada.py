"""Add invertido field to lampada table

Revision ID: 3f8a9c2b5d1e
Revises: d15eff8184a8
Create Date: 2025-12-09 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f8a9c2b5d1e'
down_revision: Union[str, None] = 'd15eff8184a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add invertido column to lampada table."""
    # Add invertido column with default value False
    op.add_column('lampada', sa.Column('invertido', sa.Boolean(), nullable=False, server_default='0'))


def downgrade() -> None:
    """Remove invertido column from lampada table."""
    op.drop_column('lampada', 'invertido')
