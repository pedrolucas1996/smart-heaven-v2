"""add house id no user

Revision ID: f2a493ce5769
Revises: 01503a0dc8c5
Create Date: 2025-12-10 13:51:46.817803

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'f2a493ce5769'
down_revision: Union[str, None] = '01503a0dc8c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('users', sa.Column('id_house', sa.Integer(), nullable=False))

def downgrade():
    op.drop_column('users', 'id_house')