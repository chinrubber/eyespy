"""empty message

Revision ID: 989d5d742b60
Revises: 114fca625728
Create Date: 2017-12-18 05:46:46.587255

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '989d5d742b60'
down_revision = '114fca625728'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('device', schema=None) as batch_op:
        batch_op.add_column(sa.Column('important', sa.Boolean(), server_default=sa.sql.expression.literal(False), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('device', schema=None) as batch_op:
        batch_op.drop_column('important')

    # ### end Alembic commands ###
