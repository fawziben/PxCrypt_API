"""add the time residency field to admin groups

Revision ID: b60c41c88a0c
Revises: f9f25d31205f
Create Date: 2024-08-01 23:06:01.080504

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b60c41c88a0c'
down_revision: Union[str, None] = 'f9f25d31205f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ajout de la colonne time_residency avec une valeur par défaut de 7
    op.add_column('admin_groups', sa.Column('time_residency', sa.Integer, nullable=False, server_default='7'))

def downgrade() -> None:
    # Suppression de la colonne time_residency lors du downgrade
    op.drop_column('admin_groups', 'time_residency')
