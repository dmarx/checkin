"""server autopopulates checkin audit fields

Revision ID: e9c2d8596950
Revises: 
Create Date: 2021-01-30 14:18:21.948641

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e9c2d8596950'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('checkins', sa.Column('created_datetime', sa.DateTime(timezone=True), nullable=True))
    op.add_column('checkins', sa.Column('updated_datetime', sa.DateTime(timezone=True), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('checkins', 'updated_datetime')
    op.drop_column('checkins', 'created_datetime')
    # ### end Alembic commands ###
