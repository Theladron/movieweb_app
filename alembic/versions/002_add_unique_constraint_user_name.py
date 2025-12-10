"""add unique constraint to user name

Revision ID: 002
Revises: 001
Create Date: 2025-12-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint('uq_user_name', 'user', ['name'])


def downgrade() -> None:
    op.drop_constraint('uq_user_name', 'user', type_='unique')


