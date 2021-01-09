from pydantic import BaseModel


class LookedButtonData(BaseModel):
    id_user: int
    id_tv_show: int
    id_episode: int
    episode_number: int
    season_number: int
    looked: bool

    def __init__(self, id_user, id_tv_show, id_episode, episode_number, season_number, looked):
        super(LookedButtonData, self).__init__(
            id_user=int(id_user),
            id_tv_show=int(id_tv_show),
            id_episode=int(id_episode),
            episode_number=int(episode_number),
            season_number=int(season_number),
            looked=bool(int(looked))
        )
