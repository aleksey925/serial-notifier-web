from pydantic import BaseModel


class UserEpisodeSchema(BaseModel):
    id_episode: int
    looked: bool
