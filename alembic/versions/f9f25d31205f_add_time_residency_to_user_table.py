"""add time residency to user table

Revision ID: f9f25d31205f
Revises: 89a486228c7e
Create Date: 2024-08-01 00:42:44.629034

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f9f25d31205f'
down_revision: Union[str, None] = '89a486228c7e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ajoute la colonne time_residency à la table users
    op.add_column('users', sa.Column('time_residency', sa.Integer(), nullable=False, server_default='2'))

def downgrade() -> None:
    # Supprime la colonne time_residency de la table users
    op.drop_column('users', 'time_residency')