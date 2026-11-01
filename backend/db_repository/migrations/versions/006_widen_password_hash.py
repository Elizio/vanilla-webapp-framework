"""Widen users.password_hash from String(128) to String(255).

Werkzeug's default scrypt ``generate_password_hash`` output is about 162
characters. VARCHAR(128) is accepted by SQLite (length is ignored) but
fails or truncates on Postgres. This revision only changes the column
type; it does not rewrite rows.

Downgrade narrows the column back to 128. That can fail if any stored
hash is longer than 128 characters (Postgres/MySQL will reject the
ALTER; SQLite will keep the data because it ignores VARCHAR length).

Revision ID: 006
Revises: 005
Create Date: 2026-11-01
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column(
            'password_hash',
            existing_type=sa.String(length=128),
            type_=sa.String(length=255),
            existing_nullable=True,
        )


def downgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column(
            'password_hash',
            existing_type=sa.String(length=255),
            type_=sa.String(length=128),
            existing_nullable=True,
        )
