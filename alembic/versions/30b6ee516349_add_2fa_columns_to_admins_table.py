"""add 2fa columns to admins table

Revision ID: 30b6ee516349
Revises: c390582c2eaa
Create Date: 2024-08-05 14:03:00.809294

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '30b6ee516349'
down_revision: Union[str, None] = 'c390582c2eaa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ajout des colonnes verification_code et code_expiry à la table admins
    op.add_column('admins', sa.Column('verification_code', sa.String(), nullable=True))
    op.add_column('admins', sa.Column('code_expiry', sa.DateTime(), nullable=True))

def downgrade() -> None:
    # Suppression des colonnes verification_code et code_expiry de la table admins
    op.drop_column('admins', 'verification_code')
    op.drop_column('admins', 'code_expiry')