"""add 2FA column

Revision ID: d2026f7583d3
Revises: 5a4331b4758a
Create Date: 2024-07-08 22:25:49.061776

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd2026f7583d3'
down_revision: Union[str, None] = '5a4331b4758a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('users', sa.Column('TFA', sa.Boolean, nullable=False, server_default=sa.sql.expression.true()))

def downgrade() -> None:
    op.drop_column('users', 'TFA')
