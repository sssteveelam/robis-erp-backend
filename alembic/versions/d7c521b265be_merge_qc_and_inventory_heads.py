"""merge qc and inventory heads

Revision ID: d7c521b265be
Revises: 49c028d401eb, f2c1d0a12345
Create Date: 2025-11-29 11:08:20.083464

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd7c521b265be'
down_revision: Union[str, None] = ('49c028d401eb', 'f2c1d0a12345')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
