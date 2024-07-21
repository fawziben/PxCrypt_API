"""Add state column to user

Revision ID: a25476a55ca9
Revises: d2026f7583d3
Create Date: 2024-07-16 01:46:05.439302

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a25476a55ca9'
down_revision: Union[str, None] = 'd2026f7583d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users',sa.Column('state', sa.Boolean, nullable=False, server_default=sa.sql.expression.true()))
    pass


def downgrade() -> None:
    op.drop_column('users','state')
    pass
