from datetime import datetime, timedelta

import jwt

from config import get_config

config = get_config()


def get_token(user_id: int) -> str:
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(minutes=config.JWT_EXP_DELTA_MIN)
    }
    return jwt.encode(
        payload=payload, key=config.JWT_SECRET, algorithm=config.JWT_ALGORITHM
    ).decode('utf-8')
