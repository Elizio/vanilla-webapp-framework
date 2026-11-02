"""Add users.token_version for server-side JWT revocation.

Integer NOT NULL default 0. Existing rows stay at 0 so in-flight JWTs
without a ``tv`` claim remain valid after deploy. Logout (and later
password reset / logout-all) increment the column. Downgrade drops it.

Revision ID: 008
Revises: 007
Create Date: 2026-11-02
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '008'
down_revision: Union[str, None] = '007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(
            sa.Column(
                'token_version',
                sa.Integer(),
                nullable=False,
                server_default='0',
            )
        )


def downgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('token_version')
