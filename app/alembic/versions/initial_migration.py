
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String(50)),
        sa.Column("full_name", sa.String(50)),
    )

def downgrade():
    op.drop_table("users")
