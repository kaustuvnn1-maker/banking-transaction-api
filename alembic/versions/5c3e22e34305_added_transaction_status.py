"""added transaction_status

Revision ID: 5c3e22e34305
Revises: 1f01083ad5de
Create Date: 2026-08-30 23:05:47.087510

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5c3e22e34305'
down_revision: Union[str, Sequence[str], None] = '1f01083ad5de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'transactions',
        sa.Column(
            'transaction_status',
            sa.String(length=20),
            server_default='FAILURE',
            nullable=False,
        ),
    )

    op.execute(
        "UPDATE transactions SET transaction_status = 'SUCCESS'"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('transactions', 'transaction_status')
