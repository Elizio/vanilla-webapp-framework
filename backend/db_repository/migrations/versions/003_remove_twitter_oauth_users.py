"""Remove Twitter OAuth user records

Revision ID: 003
Revises: 002
Create Date: 2026-06-19

"""
from typing import Sequence, Union

from alembic import op

revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DELETE FROM users WHERE oauth_provider = 'twitter'")


def downgrade() -> None:
    pass
