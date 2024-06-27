"""create src img column

Revision ID: 3827fa15e9ce
Revises: 900509063c68
Create Date: 2024-06-27 01:57:25.431488

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3827fa15e9ce'
down_revision: Union[str, None] = '900509063c68'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('img_src',sa.String, nullable=True))
    pass


def downgrade() -> None:
    op.drop_column('users','img_src')
    pass
