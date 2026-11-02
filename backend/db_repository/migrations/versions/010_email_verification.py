"""Add email verification columns, unique emails, and auth_tokens.

Lowercases existing emails, keeps the lowest id in each duplicate group
and NULLs the rest (OAuth accounts still sign in through their provider),
then adds ``uq_users_email``. Pre-existing users get
``verification_exempt=true`` so they keep logging in. Downgrade drops
the unique constraint, the new columns, and ``auth_tokens``.

Revision ID: 010
Revises: 009
Create Date: 2026-11-02
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

revision: str = '010'
down_revision: Union[str, None] = '009'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(
            sa.Column(
                'email_verified',
                sa.Boolean(),
                nullable=False,
                server_default='0',
            )
        )
        batch_op.add_column(
            sa.Column(
                'email_verified_at',
                sa.DateTime(),
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                'verification_exempt',
                sa.Boolean(),
                nullable=False,
                server_default='0',
            )
        )

    bind = op.get_bind()
    bind.execute(
        text(
            "UPDATE users SET email = lower(trim(email)) "
            "WHERE email IS NOT NULL AND trim(email) != ''"
        )
    )
    bind.execute(
        text(
            "UPDATE users SET email = NULL WHERE email IS NOT NULL AND trim(email) = ''"
        )
    )
    bind.execute(
        text(
            'CREATE TEMP TABLE _keep_email AS '
            'SELECT MIN(id) AS id FROM users WHERE email IS NOT NULL GROUP BY email'
        )
    )
    dup_count = bind.execute(
        text(
            'SELECT COUNT(*) FROM users '
            'WHERE email IS NOT NULL AND id NOT IN (SELECT id FROM _keep_email)'
        )
    ).scalar()
    bind.execute(
        text(
            'UPDATE users SET email = NULL '
            'WHERE email IS NOT NULL AND id NOT IN (SELECT id FROM _keep_email)'
        )
    )
    bind.execute(text('DROP TABLE _keep_email'))
    bind.execute(text('UPDATE users SET verification_exempt = 1'))
    if dup_count:
        print(f'010_email_verification: nulled {dup_count} duplicate email rows')

    with op.batch_alter_table('users') as batch_op:
        batch_op.create_unique_constraint('uq_users_email', ['email'])

    op.create_table(
        'auth_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('purpose', sa.String(length=16), nullable=False),
        sa.Column('token_hash', sa.String(length=64), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('used_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_hash', name='uq_auth_tokens_token_hash'),
    )
    op.create_index('ix_auth_tokens_user_id', 'auth_tokens', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_auth_tokens_user_id', table_name='auth_tokens')
    op.drop_table('auth_tokens')
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_constraint('uq_users_email', type_='unique')
        batch_op.drop_column('verification_exempt')
        batch_op.drop_column('email_verified_at')
        batch_op.drop_column('email_verified')
