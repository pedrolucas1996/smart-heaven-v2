"""add table casa

Revision ID: 01503a0dc8c5
Revises: 8b547115af5e
Create Date: 2025-12-10 13:44:21.454206

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '01503a0dc8c5'
down_revision: Union[str, None] = '8b547115af5e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'casa',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('estado', sa.String(2), nullable=False),
        sa.Column('cidade', sa.String(100), nullable=False),
        sa.Column('bairro', sa.String(100), nullable=False),
        sa.Column('rua', sa.String(100), nullable=False),
        sa.Column('numero', sa.String(20), nullable=False),
        sa.Column('complemento', sa.String(100), nullable=True),
        sa.Column('cep', sa.String(20), nullable=False),
        sa.Column('id_user', sa.Integer, nullable=False),
        sa.Column('nome', sa.String(50), nullable=False),
        sa.Column('plano', sa.String(50), nullable=False)
    )

def downgrade() -> None:
    op.drop_table('casa')
"""add table casa

Revision ID: 01503a0dc8c5
Revises: 8b547115af5e
Create Date: 2025-12-10 13:44:21.454206

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '01503a0dc8c5'
down_revision: Union[str, None] = '8b547115af5e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
