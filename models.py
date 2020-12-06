import enum
from datetime import datetime

from sqlalchemy import (
    Table, Column, Integer, DateTime, Enum as SaEnum, Unicode, Boolean, ForeignKey, UnicodeText,
    UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Sex(enum.Enum):
    MALE = 'male'
    FEMALE = 'female'


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    sex = Column(SaEnum(*[i.value for i in Sex], name='sex'))
    nick = Column(Unicode(length=50), unique=True, nullable=False)
    name = Column(Unicode(length=50))
    surname = Column(Unicode(length=50))
    password = Column(Unicode(length=70), nullable=False)
    email = Column(Unicode(length=80), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    reg_date = Column(DateTime(timezone=True), default=datetime.now())


user_table = User.__table__


# Хранит информацию о том какие сериалы отслеживает пользователь
tracked_tv_show = Table(
    'tracked_tv_show',
    metadata,
    Column('id_user', Integer, ForeignKey('user.id')),
    Column('id_tv_show', Integer, ForeignKey('tv_show.id'))
)

# Хранит данные для панели уведомлений, в которой для каждого пользователя
# отображаются недавно вышедшие серии.
tv_show_notification = Table(
    'tv_show_notification',
    metadata,
    Column('id_user', Integer, ForeignKey('user.id')),
    Column('id_episode', Integer, ForeignKey('episode.id'))
)

# Хранит дополнительную информацию о сериях. На пример, какие серии
# пользователь посмотрел.
user_episode = Table(
    'user_episode',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('id_user', Integer, ForeignKey('user.id'), nullable=False),
    Column('id_episode', Integer, ForeignKey('episode.id'), nullable=False),
    Column('looked', Boolean(), default=False),
    UniqueConstraint('id_user', 'id_episode', name='constraint_unique_episode_for_user'),
)

tv_show = Table(
    'tv_show',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', Unicode(150), nullable=False),
    Column('cover', Unicode(300)),
    Column('description', UnicodeText()),
)

episode = Table(
    'episode',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('id_tv_show', Integer, ForeignKey('tv_show.id'), nullable=False),
    Column('episode_number', Integer, nullable=False),
    Column('season_number', Integer, nullable=False),
    UniqueConstraint('id_tv_show', 'episode_number', 'season_number', name='constraint_unique_episode'),
)

source_info = Table(
    'source_info',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('site_name', Unicode(length=15), nullable=False),
    Column('encoding', Unicode(length=10)),
)

source = Table(
    'source',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('id_tv_show', Integer, ForeignKey('tv_show.id'), nullable=False),
    Column(
        'id_source_info', Integer, ForeignKey('source_info.id'), nullable=False
    ),
    Column('url', Unicode(length=300), nullable=False),
)

telegram_acc = Table(
    'telegram_acc',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('id_user', Integer, ForeignKey('user.id'), nullable=False),
    Column('chat_id', Integer, nullable=False),
    Column('username', Unicode(length=30), nullable=False),
)
