from common.jwt import get_token
from common.rest_api.exceptions import NotValidDataError
from common.security import hashing_password, check_password
from db import crete_user, get_user_by_email


async def login(db_session, data: dict) -> str:
    user = await get_user_by_email(db_session, data['email'])
    if not user:
        raise NotValidDataError(
            f'User with email={data["email"]} not exists', 'email'
        )
    if not check_password(data['password'], user['password']):
        raise NotValidDataError(
            f'The password entered is not correct', 'password'
        )

    return get_token(user['id'])


async def registration(db_session, data: dict):
    data['password'] = hashing_password(data['password'])
    await crete_user(db_session, data)
