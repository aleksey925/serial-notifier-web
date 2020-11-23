from datetime import datetime

from sqlalchemy import (
    MetaData, Table, Column, Integer, DateTime, Enum, Unicode, Boolean,
    ForeignKey, UnicodeText
)

metadata = MetaData()

SEX = ('male', 'female')

user = Table(
    'user',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('sex', Enum(*SEX, name='sex')),
    Column('nick', Unicode(length=50), unique=True, nullable=False),
    Column('name', Unicode(length=50)),
    Column('surname', Unicode(length=50),),
    Column('password', Unicode(length=70), nullable=False),
    Column('email', Unicode(length=80), unique=True, nullable=False),
    Column('is_active', Boolean, default=True),
    Column('reg_date', DateTime(timezone=True), default=datetime.now()),
)

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
