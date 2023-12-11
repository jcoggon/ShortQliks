"""Update user_id

Revision ID: 395de3889fe6
Revises: 856c31163aa7
Create Date: 2023-12-04 15:22:20.107627

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '395de3889fe6'
down_revision: Union[str, None] = '856c31163aa7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('assigned_group',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('assigned_role',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('type', sa.String(), nullable=True),
    sa.Column('level', sa.String(), nullable=True),
    sa.Column('permissions', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('qlik_user',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('tenantId', sa.String(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('lastUpdated', sa.DateTime(), nullable=True),
    sa.Column('qlik_app_link', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_group_association',
    sa.Column('user_id', sa.String(), nullable=True),
    sa.Column('group_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['assigned_group.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['qlik_user.id'], )
    )
    op.create_table('user_role_association',
    sa.Column('user_id', sa.String(), nullable=True),
    sa.Column('role_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['assigned_role.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['qlik_user.id'], )
    )
    op.add_column('user', sa.Column('user_id', sa.String(), nullable=True))
    op.drop_column('user', '_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('_id', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('user', 'user_id')
    op.drop_table('user_role_association')
    op.drop_table('user_group_association')
    op.drop_table('qlik_user')
    op.drop_table('assigned_role')
    op.drop_table('assigned_group')
    # ### end Alembic commands ###
