"""add_constraint_unique_episode_for_user_in_user_episode

Revision ID: 67cf23606710
Revises: a3600a14efae
Create Date: 2020-11-30 09:44:11.028097

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '67cf23606710'
down_revision = 'a3600a14efae'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('constraint_unique_episode_for_user', 'user_episode', ['id_user', 'id_episode'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('constraint_unique_episode_for_user', 'user_episode', type_='unique')
    # ### end Alembic commands ###
