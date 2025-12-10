"""id_house nullable

Revision ID: b9720db985f1
Revises: 24c2f294d27d
Create Date: 2025-12-10 19:05:35.542638

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'b9720db985f1'
down_revision: Union[str, None] = '24c2f294d27d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Limpar migração: apenas tornar id_house nullable em users
    op.alter_column('users', 'id_house', nullable=True, existing_type=mysql.INTEGER(display_width=11))


def downgrade() -> None:
    # Limpar downgrade: reverter id_house para not nullable em users
    op.alter_column('users', 'id_house', nullable=False, existing_type=mysql.INTEGER(display_width=11))
