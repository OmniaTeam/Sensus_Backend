"""empty message

Revision ID: eb7d7e55bb23
Revises: 6901f2b7b85f
Create Date: 2024-02-07 01:39:24.621528

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eb7d7e55bb23'
down_revision: Union[str, None] = '6901f2b7b85f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('enabled', sa.Boolean(), nullable=False))
    op.drop_column('users', 'disabled')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('disabled', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.drop_column('users', 'enabled')
    # ### end Alembic commands ###
