"""Add OAuth columns to users table

Revision ID: 002
Revises: 001
Create Date: 2026-06-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('email', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('oauth_provider', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('oauth_id', sa.String(length=255), nullable=True))
        batch_op.alter_column('password_hash', existing_type=sa.String(length=128), nullable=True)
        batch_op.create_unique_constraint('uq_oauth', ['oauth_provider', 'oauth_id'])


def downgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_constraint('uq_oauth', type_='unique')
        batch_op.alter_column('password_hash', existing_type=sa.String(length=128), nullable=False)
        batch_op.drop_column('oauth_id')
        batch_op.drop_column('oauth_provider')
        batch_op.drop_column('email')
