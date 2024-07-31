"""Add ON DELETE CASCADE to sfiles.id_file

Revision ID: 89a486228c7e
Revises: a25476a55ca9
Create Date: 2024-07-31 01:56:21.706621

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '89a486228c7e'
down_revision: Union[str, None] = 'a25476a55ca9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Suppression de l'ancienne contrainte de clé étrangère
    op.drop_constraint('sfiles_id_file_fkey', 'sfiles', type_='foreignkey')

    # Ajout de la nouvelle contrainte de clé étrangère avec ON DELETE CASCADE
    op.create_foreign_key(
        'sfiles_id_file_fkey',
        'sfiles', 'ufiles',
        ['id_file'], ['id'],
        ondelete='CASCADE'
    )

def downgrade():
    # Suppression de la nouvelle contrainte de clé étrangère
    op.drop_constraint('sfiles_id_file_fkey', 'sfiles', type_='foreignkey')

    # Ajout de l'ancienne contrainte de clé étrangère sans ON DELETE CASCADE
    op.create_foreign_key(
        'sfiles_id_file_fkey',
        'sfiles', 'ufiles',
        ['id_file'], ['id']
    )
