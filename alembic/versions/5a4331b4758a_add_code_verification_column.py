"""add code verification column

Revision ID: 5a4331b4758a
Revises: 3827fa15e9ce
Create Date: 2024-07-01 05:03:56.044883

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5a4331b4758a'
down_revision: Union[str, None] = '3827fa15e9ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('verification_code',sa.String, nullable=True))
    op.add_column('users',sa.Column('code_expiry',sa.DateTime, nullable=True))
    pass


def downgrade() -> None:
    op.drop_column('users','verification_code')
    op.drop_column('users','code_expiry')

    pass
