"""add_constraint_unique_episode

Revision ID: a3600a14efae
Revises: f87d27f7d9f8
Create Date: 2020-11-29 15:58:32.570319

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'a3600a14efae'
down_revision = 'f87d27f7d9f8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(
        'constraint_unique_episode', 'episode', ['id_tv_show', 'episode_number', 'season_number']
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('constraint_unique_episode', 'episode', type_='unique')
    # ### end Alembic commands ###