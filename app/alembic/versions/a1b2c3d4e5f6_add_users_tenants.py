
"""Add users, tenants tables and link tenants to tasks

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2023-08-14

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('email', sa.String, unique=True, index=True, nullable=False),
        sa.Column('hashed_password', sa.String, nullable=False),
        sa.Column('api_key', sa.String, nullable=True)
    )
    
    # Create tenants table
    op.create_table(
        'tenants',
        sa.Column('tenant_id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('tenant_name', sa.String, index=True, nullable=False),
        sa.Column('qlik_cloud_key', sa.String, nullable=True)
    )

    # Add tenant_id to tasks table to link tenants to tasks
    op.add_column('tasks', sa.Column('tenant_id', sa.Integer, sa.ForeignKey('tenants.tenant_id')))


def downgrade():
    op.drop_column('tasks', 'tenant_id')
    op.drop_table('tenants')
    op.drop_table('users')
