import logging
from typing import Optional

import asyncpgsa
from asyncpg import UniqueViolationError, Record

from common.rest_api.exceptions import NotValidDataError
from models import user

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
