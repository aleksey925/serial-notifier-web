import typing as t

from pydantic.main import BaseModel


class TvShowSchema(BaseModel):
    tv_shows: t.Dict[str, t.Dict[str, t.Dict[str, bool]]]


class UserEpisodeReqSchema(BaseModel):
    id_episode: int
    looked: bool


class UserEpisodeRespSchema(UserEpisodeReqSchema):
    id: int
