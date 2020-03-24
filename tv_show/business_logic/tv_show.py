from db import get_user_tv_show
from tv_show.schemas import TvShow

tv_show_schema = TvShow()


async def get_all_user_tv_show(db_session, user_id: int) -> str:
    user_tv_show = await get_user_tv_show(db_session, user_id)

    data = []
    for rec in user_tv_show:
        data.append({
            'name': rec['name'],
            'season_number': rec['season_number'],
            'episode_number': rec['episode_number'],
            'looked': bool(rec['looked']),
        })

    return tv_show_schema.dumps(data, many=True)
