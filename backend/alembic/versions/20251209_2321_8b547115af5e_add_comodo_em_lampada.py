"""add comodo em lampada

Revision ID: 8b547115af5e
Revises: 6942f735cdd1
Create Date: 2025-12-09 23:21:10.855225

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '8b547115af5e'
down_revision: Union[str, None] = '6942f735cdd1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.add_column('lampada', sa.Column('comodo', sa.String(length=50), nullable=True))

def downgrade():
    op.drop_column('lampada', 'comodo')
