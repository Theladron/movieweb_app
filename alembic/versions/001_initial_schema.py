"""initial schema

Revision ID: 001
Revises: 
Create Date: 2025-12-10 01:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create user table
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create movie table
    op.create_table(
        'movie',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('release_year', sa.Integer(), nullable=True),
        sa.Column('poster', sa.String(), nullable=True),
        sa.Column('director', sa.String(), nullable=True),
        sa.Column('rating', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create user_movies linking table
    op.create_table(
        'user_movies',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('movie_id', sa.Integer(), nullable=False),
        sa.Column('user_rating', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['movie_id'], ['movie.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('user_movies')
    op.drop_table('movie')
    op.drop_table('user')

