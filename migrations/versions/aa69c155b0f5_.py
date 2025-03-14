"""empty message

Revision ID: aa69c155b0f5
Revises: f04e18bf4f75
Create Date: 2025-03-14 12:00:03.188514

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aa69c155b0f5'
down_revision: Union[str, None] = 'f04e18bf4f75'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
