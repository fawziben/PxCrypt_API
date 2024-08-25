"""Add new columns to admin_parameters

Revision ID: 2d1b73f02ae7
Revises: 6e14dce6e8eb
Create Date: 2024-08-25 03:54:25.441153

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d1b73f02ae7'
down_revision: Union[str, None] = '6e14dce6e8eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ajouter les nouvelles colonnes
    op.add_column('admin_parameters', sa.Column('all_domains', sa.Boolean(), nullable=True, server_default=sa.text('TRUE')))
    op.add_column('admin_parameters', sa.Column('all_extensions', sa.Boolean(), nullable=True, server_default=sa.text('TRUE')))
    op.add_column('admin_parameters', sa.Column('verification_code', sa.String(), nullable=True))
    op.add_column('admin_parameters', sa.Column('code_expiry', sa.Integer(), nullable=True))
    pass

def downgrade() -> None:
    # Supprimer les colonnes ajoutées
    op.drop_column('admin_parameters', 'all_domains')
    op.drop_column('admin_parameters', 'all_extensions')
    op.drop_column('admin_parameters', 'verification_code')
    op.drop_column('admin_parameters', 'code_expiry')
    pass