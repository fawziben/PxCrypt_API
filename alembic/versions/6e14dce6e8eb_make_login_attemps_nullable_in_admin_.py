"""make login attemps nullable in admin parameters

Revision ID: 6e14dce6e8eb
Revises: d3d4560430c0
Create Date: 2024-08-21 01:50:33.521487

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e14dce6e8eb'
down_revision: Union[str, None] = 'd3d4560430c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Modification de la colonne login_attempt pour la rendre nullable
    op.alter_column(
        'admin_parameters',
        'login_attempt',
        existing_type=sa.String(),
        nullable=True
    )
    pass

def downgrade() -> None:
    # Revenir en arrière pour rendre la colonne non nullable
    op.alter_column(
        'admin_parameters',
        'login_attempt',
        existing_type=sa.String(),
        nullable=False
    )
    pass