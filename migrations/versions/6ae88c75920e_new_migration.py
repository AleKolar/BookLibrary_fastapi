"""new migration

Revision ID: 6ae88c75920e
Revises: d6e2322449b1
Create Date: 2025-02-03 20:31:06.926055

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ae88c75920e'
down_revision: Union[str, None] = 'd6e2322449b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
