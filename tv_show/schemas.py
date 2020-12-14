import typing as t

from pydantic.main import BaseModel


class TvShowSchema(BaseModel):
    tv_shows: t.Dict[str, t.Dict[str, t.List[int]]]
