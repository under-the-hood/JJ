"""empty message

Revision ID: 5506689d8fe0
Revises: 9b0c96ff9c52
Create Date: 2026-10-17 09:53:29.484638

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5506689d8fe0'
down_revision: Union[str, Sequence[str], None] = '9b0c96ff9c52'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
