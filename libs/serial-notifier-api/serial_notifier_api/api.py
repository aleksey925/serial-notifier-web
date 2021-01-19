from datetime import datetime, timedelta
from urllib.parse import urljoin

import requests
from jose import jwt
from jose.constants import ALGORITHMS

from serial_notifier_schema.tv_show import UserEpisodeReqSchema


def create_access_token(data: dict, secret: str, exp_delta_min: int = 60, algorithm=ALGORITHMS.HS256) -> str:
    token_data = data.copy()
    token_data.update(
        {
            "exp": datetime.utcnow() + timedelta(minutes=exp_delta_min)
        }
    )
    return jwt.encode(token_data, secret, algorithm=algorithm)


class Client:
    def __init__(
            self,
            base_url: str,
            user_id: int,
            jwt_secret: str,
            jwt_exp_delta_min: int = 60,
            jwt_algorithm=ALGORITHMS.HS256
    ):
        self.base_url = base_url
        self.user_id = user_id
        self.jwt_secret = jwt_secret
        self.jwt_exp_delta_min = jwt_exp_delta_min
        self.jwt_algorithm = jwt_algorithm

        self._jwt_token = create_access_token(
            data={"user_id": user_id},
            secret=jwt_secret,
            exp_delta_min=jwt_exp_delta_min,
            algorithm=jwt_algorithm
        )
        self._session = requests.session()
        self._session.headers.update(
            {
                'Authorization': f'Bearer {self._jwt_token}'
            }
        )

    def update_user_episode(self, episode_info: UserEpisodeReqSchema):
        resp = self._session.post(
            url=urljoin(self.base_url, f'/tv_show/episode/{episode_info.id_episode}/'),
            json=episode_info.dict(),
        )
        resp.raise_for_status()
