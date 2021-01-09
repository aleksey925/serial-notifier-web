from datetime import datetime, timedelta
from urllib.parse import urljoin

import requests
from jose import jwt

from bot.config import get_config
from serial_notifier_web.schema import UserEpisodeSchema

config = get_config()


def create_access_token(data: dict) -> str:
    token_data = data.copy()
    token_data.update(
        {
            "exp": datetime.utcnow() + timedelta(minutes=config.JWT_EXP_DELTA_MIN)
        }
    )
    return jwt.encode(token_data, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)


class Client:
    def __init__(self, base_url: str, user_id: int):
        self.base_url = base_url
        self.user_id = user_id

        self.session = requests.session()
        self.session.headers.update({'Authorization': f'Bearer {create_access_token({"user_id": user_id})}'})

    def update_user_episode(self, episode_info: UserEpisodeSchema):
        resp = self.session.post(
            url=urljoin(self.base_url, f'/tv_show/episode/{episode_info.id_episode}/'),
            json=episode_info.dict(),
        )
        resp.raise_for_status()
