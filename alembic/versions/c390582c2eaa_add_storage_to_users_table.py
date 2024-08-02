"""add storage to users table

Revision ID: c390582c2eaa
Revises: b60c41c88a0c
Create Date: 2024-08-02 02:51:40.039058

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c390582c2eaa'
down_revision: Union[str, None] = 'b60c41c88a0c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Conversion de 100 Mo en bits
DEFAULT_STORAGE_BITS = 100 * 1024 * 1024 * 8

def upgrade() -> None:
    # Ajout de la colonne storage avec une valeur par défaut de 100 Mo (en bits)
    op.add_column('users', sa.Column('storage', sa.BigInteger, nullable=False, server_default=str(DEFAULT_STORAGE_BITS)))

def downgrade() -> None:
    # Suppression de la colonne storage lors du downgrade
    op.drop_column('users', 'storage')