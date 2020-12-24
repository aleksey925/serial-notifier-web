import typing as t

from pydantic.main import BaseModel


class TvShowSchema(BaseModel):
    tv_shows: t.Dict[str, t.Dict[str, t.List[int]]]


class UserEpisodeReqSchema(BaseModel):
    id_user: int
    id_episode: int
    looked: bool


class UserEpisodeRespSchema(UserEpisodeReqSchema):
    id: int
