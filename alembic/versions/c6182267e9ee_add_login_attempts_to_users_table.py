"""add login attempts to users table

Revision ID: c6182267e9ee
Revises: 30b6ee516349
Create Date: 2024-08-21 00:11:51.887971
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c6182267e9ee'
down_revision: Union[str, None] = '30b6ee516349'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('users', sa.Column('attempts', sa.Integer, nullable=False, server_default='0'))

def downgrade() -> None:
    op.drop_column('users', 'attempts')
