import psycopg2.errors
import sqlalchemy.orm.exc
from structlog import get_logger

from apps.auth.exceptions import CredentialsNotValid, UserAlreadyExists
from apps.auth.security import check_password, create_access_token, hashing_password
from config import get_config
from db import get_db
from models import User, user_table

config = get_config()
logger = get_logger('auth')


class AccountService:
    def __init__(self):
        self.db = get_db()

    async def _crete_user(self, data: dict) -> dict:
        data['password'] = hashing_password(data['password'])
        try:
            new_user = await self.db.fetch_one(
                user_table.insert()
                .values(**data)
                .returning(
                    user_table.c.id,
                    user_table.c.email,
                    user_table.c.sex,
                    user_table.c.nick,
                    user_table.c.name,
                    user_table.c.surname,
                )
            )
        except psycopg2.errors.UniqueViolation as exc:
            logger.warn('Не удалось создать нового пользователя', email=data['email'], nick=data['nick'], exc_info=True)
            not_uniq_field = exc.diag.constraint_name.replace(f'{exc.diag.table_name}_', '').replace('_key', '')
            raise UserAlreadyExists(not_uniq_field) from exc

        return dict(new_user)

    async def _authenticate_user(self, email: str, password: str) -> User:
        try:
            usr = await self.db.query(User).filter(User.email == email).one()
        except sqlalchemy.orm.exc.NoResultFound:
            logger.info('Пользователь не существует, авторизация невозможна', email=email)
            raise CredentialsNotValid('User not exists')

        if not check_password(password, usr.password):
            logger.info('Введенный пароль не валиден', email=email)
            raise CredentialsNotValid('The password entered is not correct')

        return usr

    async def login(self, data) -> str:
        usr = await self._authenticate_user(data.email, data.password)
        return create_access_token(
            {'user_id': usr.id}, config.JWT_SECRET, config.JWT_EXP_DELTA_MIN, config.JWT_ALGORITHM
        )

    async def registration(self, data) -> dict:
        usr_data = dict(data)
        usr_data['sex'] = data.sex.value if data.sex else None
        return await self._crete_user(usr_data)
