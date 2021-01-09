from datetime import datetime, timedelta

import bcrypt
from asyncom import OMDatabase
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from jose.constants import ALGORITHMS
from structlog import get_logger

from config import get_config
from db import get_db
from models import User

logger = get_logger('auth')
config = get_config()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token/")


def hashing_password(raw_password: str) -> str:
    return bcrypt.hashpw(raw_password.encode(), bcrypt.gensalt()).decode()


def check_password(raw_password: str, hashed_password) -> bool:
    return bcrypt.checkpw(raw_password.encode(), hashed_password.encode())


def create_access_token(data: dict, secret: str, exp_delta_min: int = 60, algorithm=ALGORITHMS.HS256) -> str:
    token_data = data.copy()
    token_data.update(
        {
            "exp": datetime.utcnow() + timedelta(minutes=exp_delta_min)
        }
    )
    return jwt.encode(token_data, secret, algorithm=algorithm)


async def get_current_user(token: str = Depends(oauth2_scheme), db: OMDatabase = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            logger.warn('В jwt токене не была найден id пользователя')
            raise credentials_exception
    except JWTError:
        logger.warn('Возникла ошибка при попытке декодировать jwt токен', exc_info=True)
        raise credentials_exception

    usr = await db.query(User).filter(User.id == user_id).one_or_none()
    if usr is None:
        logger.warn('Пользователь не был найден, авторизация невозможна', user_id=user_id, exc_info=True)
        raise credentials_exception

    return usr
