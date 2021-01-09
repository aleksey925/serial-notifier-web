import typing as t
from dataclasses import dataclass

import asyncom
from asyncom import OMDatabase
from structlog import get_logger

from apps.common.asyncom import _get_prefixes_patch
from config import get_config

logger = get_logger(__name__)
config = get_config()

_inst = {}


def get_db() -> t.Optional[OMDatabase]:
    return _inst.get('db')


def set_db(db: OMDatabase):
    _inst['db'] = db


async def init_db():
    asyncom.om.get_prefixes = _get_prefixes_patch
    db = OMDatabase(config.DATABASE_URI, force_rollback=config.CURRENT_ENV == 'test')
    await db.connect()
    set_db(db)
    return db


async def close_db():
    db = get_db()
    await db.disconnect()


@dataclass
class UpdatedTvShow:
    id_episode: int
    id_tv_show: int
    episode_number: int
    season_number: int
