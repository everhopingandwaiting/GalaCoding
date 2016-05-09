"""empty message

Revision ID: 6f0a6b979be9
Revises: b88893abad4d
Create Date: 2016-05-09 15:51:42.093000

"""

# revision identifiers, used by Alembic.
revision = '6f0a6b979be9'
down_revision = 'b88893abad4d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('remarkposts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.Column('attitude', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_remarkposts_owner_id'), 'remarkposts', ['owner_id'], unique=False)
    op.create_index(op.f('ix_remarkposts_post_id'), 'remarkposts', ['post_id'], unique=False)
    op.add_column(u'posts', sa.Column('viewed_count', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column(u'posts', 'viewed_count')
    op.drop_index(op.f('ix_remarkposts_post_id'), table_name='remarkposts')
    op.drop_index(op.f('ix_remarkposts_owner_id'), table_name='remarkposts')
    op.drop_table('remarkposts')
    ### end Alembic commands ###