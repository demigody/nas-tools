"""3.3.16

Revision ID: 532e45e74cc0
Revises: eb3437042cc8
Create Date: 2024-04-15 05:13:43.753754

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '532e45e74cc0'
down_revision = 'eb3437042cc8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    try:
        with op.batch_alter_table('CONFIG_SITE') as batch_op:
            batch_op.add_column(sa.Column('APIKEY', sa.TEXT(), nullable=True))
    except Exception as e:
        pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
