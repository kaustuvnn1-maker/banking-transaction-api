"""create user login table

Revision ID: 9b82d5e41c30
Revises: 7a4c9e2d1f6b
Create Date: 2026-09-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9b82d5e41c30'
down_revision: Union[str, Sequence[str], None] = '7a4c9e2d1f6b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'userLogin',
        sa.Column('userID', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('userID'),
        sa.UniqueConstraint('username'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('userLogin')