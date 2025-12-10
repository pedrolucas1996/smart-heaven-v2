"""add_apelido_to_lampada

Revision ID: 5e82a13e85ca
Revises: 3f8a9c2b5d1e
Create Date: 2025-12-09 18:13:34.444798

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5e82a13e85ca'
down_revision: Union[str, None] = '3f8a9c2b5d1e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add apelido column to lampada table
    op.add_column('lampada', sa.Column('apelido', sa.String(length=50), nullable=True))


def downgrade() -> None:
    # Remove apelido column from lampada table
    op.drop_column('lampada', 'apelido')
