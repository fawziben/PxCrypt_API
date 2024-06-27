"""create a test table 

Revision ID: 900509063c68
Revises: 
Create Date: 2024-06-27 01:45:13.767826

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '900509063c68'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('test', sa.Column('id', sa.Integer,nullable=False, primary_key=True), sa.Column('description', sa.String))
    pass 


def downgrade() -> None:
    op.drop_table('test')
    pass
