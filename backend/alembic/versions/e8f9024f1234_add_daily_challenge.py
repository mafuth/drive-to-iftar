"""Add daily challenge fields

Revision ID: e8f9024f1234
Revises: d72e0788541e
Create Date: 2026-02-19 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8f9024f1234'
down_revision: Union[str, Sequence[str], None] = '60280a11fb03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('dates_collected_today', sa.Integer(), server_default='0', nullable=False))
    op.add_column('users', sa.Column('last_challenge_date', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'last_challenge_date')
    op.drop_column('users', 'dates_collected_today')
