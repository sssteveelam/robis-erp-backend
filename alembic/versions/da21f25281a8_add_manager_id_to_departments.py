"""Add manager_id to departments

Revision ID: da21f25281a8
Revises: b6401e7fc0e5
Create Date: 2025-11-12 18:56:04.352559

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "da21f25281a8"
down_revision: Union[str, None] = "b6401e7fc0e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Thêm cột manager_id (nullable=True)
    op.add_column("departments", sa.Column("manager_id", sa.Integer(), nullable=True))

    # Thêm foreign key
    op.create_foreign_key(
        "fk_departments_manager_id", "departments", "employees", ["manager_id"], ["id"]
    )


def downgrade() -> None:
    pass
