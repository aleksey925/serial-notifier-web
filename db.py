import logging
import typing
from typing import Optional

import asyncpgsa
from asyncpg import UniqueViolationError, Record
from sqlalchemy import select

from common.rest_api.exceptions import NotValidDataError
from db_datacalss import SourceData
from models import (
    user, tv_show, episode, tracked_tv_show, user_episode, source, source_info
)

logger = logging.getLogger()


async def init_db(app):
    pool = await asyncpgsa.create_pool(dsn=app['config'].DATABASE_URI)
    app['db_pool'] = pool
    return pool


async def get_user_by_email(conn, email: str) -> Optional[Record]:
    usr = await conn.fetch(
        user.select().where(user.c.email == email)
    )
    return usr[0] if usr else None


async def crete_user(conn, data: dict):
    stmt = user.insert().values(**data)
    try:
        await conn.execute(stmt)
    except UniqueViolationError as err:
        logger.exception('Не удалось создать нового пользователя')
        field_name = err.constraint_name \
            .replace('user_', '') \
            .replace('_key', '')
        raise NotValidDataError(
            f'User with {field_name}={data[field_name]} already exists',
            field_name
        )


async def get_source_list(conn) -> typing.List[SourceData]:
    source_stmt = select([
        source.c.id,
        source_info.c.site_name,
        tv_show.c.name.label('tv_show_name'),
        source.c.url,
        source_info.c.encoding,
    ]).select_from(
        source.join(
            source_info,
            source_info.c.id == source.c.id_source_info
        ).join(
            tv_show,
            tv_show.c.id == source.c.id_tv_show
        )
    )
    return [SourceData(**src) for src in await conn.fetch(source_stmt)]


async def get_user_tv_show(conn, user_id: int):
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

    return await conn.fetch(
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
