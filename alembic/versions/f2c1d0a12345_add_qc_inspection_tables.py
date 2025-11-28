"""
add qc inspection, defect, measurement tables

Revision ID: f2c1d0a12345
Revises: daeff9cb6740_create_orders_tables
Create Date: 2025-11-28 14:35:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f2c1d0a12345'
down_revision = 'daeff9cb6740_create_orders_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'qc_inspections',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('batch_id', sa.Integer(), sa.ForeignKey('batches.id', ondelete='CASCADE'), nullable=False),
        sa.Column('lot_size', sa.Integer(), nullable=True),
        sa.Column('inspection_level', sa.String(length=10), nullable=True),
        sa.Column('aql_critical', sa.Float(), nullable=True),
        sa.Column('aql_major', sa.Float(), nullable=True),
        sa.Column('aql_minor', sa.Float(), nullable=True),
        sa.Column('sample_size', sa.Integer(), nullable=True),
        sa.Column('accept_maj', sa.Integer(), nullable=True),
        sa.Column('reject_maj', sa.Integer(), nullable=True),
        sa.Column('accept_min', sa.Integer(), nullable=True),
        sa.Column('reject_min', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('decision', sa.String(length=20), nullable=True),
        sa.Column('owner_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'qc_defects',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('inspection_id', sa.Integer(), sa.ForeignKey('qc_inspections.id', ondelete='CASCADE'), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('severity', sa.String(length=10), nullable=False),
        sa.Column('qty', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('description', sa.Text(), nullable=True),
    )

    op.create_table(
        'qc_measurements',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('inspection_id', sa.Integer(), sa.ForeignKey('qc_inspections.id', ondelete='CASCADE'), nullable=False),
        sa.Column('characteristic', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Float(), nullable=True),
        sa.Column('unit', sa.String(length=20), nullable=True),
        sa.Column('pass_fail', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('method', sa.String(length=50), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('qc_measurements')
    op.drop_table('qc_defects')
    op.drop_table('qc_inspections')

