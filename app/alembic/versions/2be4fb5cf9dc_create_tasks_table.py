
"""Create tasks table

Revision ID: 2be4fb5cf9dc
Revises:
Create Date: 2023-08-11
"""

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('title', sa.String, index=True),
        sa.Column('status', sa.String, index=True),
    )


def downgrade():
    op.drop_table('tasks')
