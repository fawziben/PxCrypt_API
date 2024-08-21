"""add the attempts column

Revision ID: d3d4560430c0
Revises: c6182267e9ee
Create Date: 2024-08-21 00:30:56.773309

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3d4560430c0'
down_revision: Union[str, None] = 'c6182267e9ee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('attempts', sa.Integer, nullable=False, server_default='0'))

def downgrade() -> None:
    op.drop_column('users', 'attempts')