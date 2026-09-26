"""add idem_key to transactions

Revision ID: 7a4c9e2d1f6b
Revises: 5c3e22e34305
Create Date: 2026-09-23

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a4c9e2d1f6b'
down_revision: Union[str, Sequence[str], None] = '5c3e22e34305'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'transactions',
        sa.Column('idem_key', sa.String(), nullable=True, unique=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('transactions', 'idem_key')
