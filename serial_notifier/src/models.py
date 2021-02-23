import enum
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SaEnum
from sqlalchemy import ForeignKey, Integer, Table, Unicode, UnicodeText, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Sex(enum.Enum):
    MALE = 'male'
    FEMALE = 'female'


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)  # noqa: A003
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
tracked_tv_show_table = Table(
    'tracked_tv_show',
    metadata,
    Column('id_user', Integer, ForeignKey('user.id')),
    Column('id_tv_show', Integer, ForeignKey('tv_show.id')),
)


# Хранит данные для панели уведомлений, в которой для каждого пользователя
# отображаются недавно вышедшие серии.
tv_show_notification_table = Table(
    'tv_show_notification',
    metadata,
    Column('id_user', Integer, ForeignKey('user.id')),
    Column('id_episode', Integer, ForeignKey('episode.id')),
)


class TvShow(Base):
    __tablename__ = 'tv_show'

    id = Column(Integer, primary_key=True)  # noqa: A003
    name = Column(Unicode(150), nullable=False)
    cover = Column(Unicode(300))
    description = Column(UnicodeText())


tv_show_table = TvShow.__table__


class Episode(Base):
    __tablename__ = 'episode'
    __table_args__ = (
        UniqueConstraint('id_tv_show', 'episode_number', 'season_number', name='constraint_unique_episode'),
    )

    id = Column(Integer, primary_key=True)  # noqa: A003
    id_tv_show = Column(Integer, ForeignKey('tv_show.id'), nullable=False)
    episode_number = Column(Integer, nullable=False)
    season_number = Column(Integer, nullable=False)


episode_table = Episode.__table__


class UserEpisode(Base):
    """
    Хранит дополнительную информацию о сериях. На пример, какие серии пользователь посмотрел.
    """

    __tablename__ = 'user_episode'
    __table_args__ = (UniqueConstraint('id_user', 'id_episode', name='constraint_unique_episode_for_user'),)

    id = Column(Integer, primary_key=True)  # noqa: A003
    id_user = Column(Integer, ForeignKey('user.id'), nullable=False)
    id_episode = Column(Integer, ForeignKey('episode.id'), nullable=False)
    looked = Column(Boolean(), default=False)


user_episode_table = UserEpisode.__table__


class SourceInfo(Base):
    __tablename__ = 'source_info'

    id = Column(Integer, primary_key=True)  # noqa: A003
    site_name = Column(Unicode(length=15), nullable=False)
    encoding = Column(Unicode(length=10))


source_info_table = SourceInfo.__table__


class Source(Base):
    __tablename__ = 'source'

    id = Column(Integer, primary_key=True)  # noqa: A003
    id_tv_show = Column(Integer, ForeignKey('tv_show.id'), nullable=False)
    id_source_info = Column(Integer, ForeignKey('source_info.id'), nullable=False)
    url = Column(Unicode(length=300), nullable=False)


source_table = Source.__table__


class TelegramAcc(Base):
    __tablename__ = 'telegram_acc'

    id = Column(Integer, primary_key=True)  # noqa: A003
    id_user = Column(Integer, ForeignKey('user.id'), nullable=False)
    chat_id = Column(Integer, nullable=False)
    username = Column(Unicode(length=30), nullable=False)


telegram_acc_table = TelegramAcc.__table__
