"""add user_id to accounts

Revision ID: 3d8d6e4f2a1b
Revises: 9b82d5e41c30
Create Date: 2026-09-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d8d6e4f2a1b'
down_revision: Union[str, Sequence[str], None] = '9b82d5e41c30'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('accounts', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_accounts_user_id_userLogin',
        'accounts',
        'userLogin',
        ['user_id'],
        ['userID'],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_accounts_user_id_userLogin', 'accounts', type_='foreignkey')
    op.drop_column('accounts', 'user_id')
