"""Add rate_limit_counters for shared auth rate limiting.

``key`` stores ``sha256(logical_key).hexdigest()`` (64 hex chars), not
the raw username or IP. Empty counter rows only. Existing ``users`` and
billing tables are untouched. Downgrade drops this table.

Revision ID: 007
Revises: 006
Create Date: 2026-11-01
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '007'
down_revision: Union[str, None] = '006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'rate_limit_counters',
        sa.Column('scope', sa.String(length=32), nullable=False),
        sa.Column('key', sa.String(length=255), nullable=False),
        sa.Column('window_start', sa.Integer(), nullable=False),
        sa.Column('hit_count', sa.Integer(), nullable=False),
        sa.Column('expires_at', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('scope', 'key', 'window_start'),
    )
    op.create_index(
        'ix_rate_limit_counters_expires_at',
        'rate_limit_counters',
        ['expires_at'],
    )


def downgrade() -> None:
    op.drop_index(
        'ix_rate_limit_counters_expires_at',
        table_name='rate_limit_counters',
    )
    op.drop_table('rate_limit_counters')
