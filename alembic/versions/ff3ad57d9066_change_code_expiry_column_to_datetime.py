"""Change code_expiry column to DateTime

Revision ID: ff3ad57d9066
Revises: 2d1b73f02ae7
Create Date: 2024-08-26 05:05:15.106090

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff3ad57d9066'
down_revision: Union[str, None] = '2d1b73f02ae7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
    'admin_parameters',
    'code_expiry',
    existing_type=sa.Integer(),
    type_=sa.TIMESTAMP(timezone=True),
)

    pass

def downgrade() -> None:
    op.alter_column(
        'admin_parameters',
        'code_expiry',
        existing_type=sa.Integer(),
        type_=sa.TIMESTAMP(timezone=True),
    )