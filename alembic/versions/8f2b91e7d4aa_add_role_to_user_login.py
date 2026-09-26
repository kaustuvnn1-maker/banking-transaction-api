"""add role to userLogin

Revision ID: 8f2b91e7d4aa
Revises: 3d8d6e4f2a1b
Create Date: 2026-09-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8f2b91e7d4aa'
down_revision: Union[str, Sequence[str], None] = '3d8d6e4f2a1b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'userLogin',
        sa.Column('role', sa.String(), nullable=False, server_default='customer'),
    )
    op.execute("UPDATE \"userLogin\" SET role = 'customer' WHERE role IS NULL OR role = ''")
    op.alter_column('userLogin', 'role', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('userLogin', 'role')
