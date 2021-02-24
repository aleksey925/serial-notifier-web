"""add_table_for_store_serial

Revision ID: b8c8e0c4f445
Revises: 6fc9fa4a6ba3
Create Date: 2020-03-22 10:41:24.084786

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'b8c8e0c4f445'
down_revision = '6fc9fa4a6ba3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'tv_show',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(length=150), nullable=True),
        sa.Column('cover', sa.Unicode(length=300), nullable=True),
        sa.Column('description', sa.UnicodeText(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'episode',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('id_tv_show', sa.Integer(), nullable=True),
        sa.Column('episode_number', sa.Integer(), nullable=True),
        sa.Column('season_number', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['id_tv_show'],
            ['tv_show.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'source',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('id_tv_show', sa.Integer(), nullable=True),
        sa.Column('site_name', sa.Unicode(length=15), nullable=True),
        sa.Column('url', sa.Unicode(length=300), nullable=True),
        sa.Column('encoding', sa.Unicode(length=10), nullable=True),
        sa.ForeignKeyConstraint(
            ['id_tv_show'],
            ['tv_show.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'tracked_tv_show',
        sa.Column('id_user', sa.Integer(), nullable=True),
        sa.Column('id_tv_show', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['id_tv_show'],
            ['tv_show.id'],
        ),
        sa.ForeignKeyConstraint(
            ['id_user'],
            ['user.id'],
        ),
    )
    op.create_table(
        'tv_show_notification',
        sa.Column('id_user', sa.Integer(), nullable=True),
        sa.Column('id_episode', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['id_episode'],
            ['episode.id'],
        ),
        sa.ForeignKeyConstraint(
            ['id_user'],
            ['user.id'],
        ),
    )
    op.create_table(
        'user_episode',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('id_user', sa.Integer(), nullable=True),
        sa.Column('id_episode', sa.Integer(), nullable=True),
        sa.Column('looked', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ['id_episode'],
            ['episode.id'],
        ),
        sa.ForeignKeyConstraint(
            ['id_user'],
            ['user.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_episode')
    op.drop_table('tv_show_notification')
    op.drop_table('tracked_tv_show')
    op.drop_table('source')
    op.drop_table('episode')
    op.drop_table('tv_show')
    # ### end Alembic commands ###