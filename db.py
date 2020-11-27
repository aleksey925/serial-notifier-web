import logging
import typing
from dataclasses import dataclass
from typing import Optional

import aiopg.sa
import psycopg2.errors
from aiopg.sa.result import RowProxy
from sqlalchemy import select

from common.rest_api.exceptions import NotValidDataError
from models import (
    user, tv_show, episode, tracked_tv_show, user_episode, source, source_info
)

logger = logging.getLogger(__name__)


async def init_db(app):
    engine = await aiopg.sa.create_engine(dsn=app['config'].DATABASE_URI)
    app['db'] = engine
    return engine


async def close_db(app):
    app['db'].close()
    await app['db'].wait_closed()


@dataclass
class SourceData:
    id: int
    id_tv_show: int
    site_name: str
    url: str
    encoding: typing.Optional[str] = None


@dataclass
class UpdatedTvShow:
    id_episode: int
    id_tv_show: int
    episode_number: int
    season_number: int


async def get_user_by_email(conn, email: str) -> Optional[RowProxy]:
    res = await conn.execute(
        user.select().where(user.c.email == email)
    )
    return await res.fetchone()


async def crete_user(conn, data: dict):
    stmt = user.insert().values(**data)
    try:
        await conn.execute(stmt)
    except psycopg2.errors.UniqueViolation as err:
        logger.exception('Не удалось создать нового пользователя')
        column_name = err.diag.constraint_name \
            .replace(f'{err.diag.table_name}_', '') \
            .replace('_key', '')
        raise NotValidDataError(
            f'User with {column_name}={data[column_name]} already exists',
            column_name
        )


async def get_source_list(conn) -> typing.List[SourceData]:
    source_stmt = select([
        source.c.id,
        source.c.id_tv_show,
        source_info.c.site_name,
        source.c.url,
        source_info.c.encoding,
    ]).select_from(
        source.join(
            source_info,
            source_info.c.id == source.c.id_source_info
        )
    )
    res = await conn.execute(source_stmt)
    return [SourceData(**src) for src in await res.fetchall()]


async def get_user_tv_show(conn, user_id: int) -> typing.Tuple[dict, ...]:
    all_tv_show_stmt = select([
        tv_show.c.name,
        episode.c.id.label('episode_id'),
        episode.c.season_number,
        episode.c.episode_number
    ]).where(
        user.c.id == user_id
    ).select_from(
        user.join(
            tracked_tv_show,
            tracked_tv_show.c.id_user == user.c.id
        ).join(
            tv_show,
            tv_show.c.id == tracked_tv_show.c.id_tv_show
        ).join(
            episode, episode.c.id_tv_show == tv_show.c.id
        )
    ).cte('all_tv_show')

    looked_episodes_stmt = select([
        episode.c.id.label('episode_id'),
        user_episode.c.looked
    ]).where(
        user.c.id == user_id
    ).select_from(
        user.join(
            user_episode,
            user_episode.c.id_user == user.c.id
        ).join(
            episode,
            episode.c.id == user_episode.c.id_episode
        )
    ).cte('looked_episodes')

    res = await conn.execute(
        select([
            all_tv_show_stmt.c.name,
            all_tv_show_stmt.c.season_number,
            all_tv_show_stmt.c.episode_number,
            looked_episodes_stmt.c.looked
        ]).select_from(
            all_tv_show_stmt.outerjoin(
                looked_episodes_stmt,
                all_tv_show_stmt.c.episode_id == looked_episodes_stmt.c.episode_id
            )
        )
    )
    return tuple(dict(i) for i in await res.fetchall())
