import asyncio
import json

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from db import close_db, init_db
from models import Episode, Source, SourceInfo, TvShow, User, UserEpisode, tracked_tv_show_table

USER_ID = 1


async def insert_user(db):
    data = {
        'sex': 'male',
        'nick': 'nick',
        'name': 'name',
        'password': '123',
        'email': 'email@mail.ru',
        'is_active': True,
    }
    await db.execute(insert(User).values(data))


async def insert_tv_show(db, dump):
    all_tv_show_names = [{'name': i} for i in dump['all_tv_show'].keys()]
    inserted_tv_show = await db.fetch_all(insert(TvShow).values(all_tv_show_names).returning(TvShow.id, TvShow.name))
    return {i.name: i.id for i in inserted_tv_show}


async def insert_episode(db, dump, tv_show_map):
    episode_data = []
    for tv_show_name, episode_inf in dump['all_tv_show'].items():
        id_tv_show = tv_show_map[tv_show_name]
        for season_number, list_episodes in episode_inf.items():
            for episode_number in list_episodes.keys():
                episode_data.append(
                    {
                        'id_tv_show': id_tv_show,
                        'episode_number': int(episode_number),
                        'season_number': int(season_number),
                    }
                )

    await db.execute(insert(Episode).values(episode_data))


async def insert_user_episode(db, dump, tv_show_map):
    eps_info = await db.fetch_all(
        select(
            [
                TvShow.id.label('tv_show_id'),
                TvShow.name,
                Episode.id.label('episode_id'),
                Episode.episode_number,
                Episode.season_number,
            ]
        ).select_from(Episode.__table__.join(TvShow, Episode.id_tv_show == TvShow.id))
    )
    inserted_episodes = {}
    for i in eps_info:
        inserted_episodes[f'{i.tv_show_id},{i.episode_number},{i.season_number}'] = i.episode_id

    user_episodes_data = []
    for tv_show_name, episode_data in dump['all_tv_show'].items():
        for season_number, episode_list in episode_data.items():
            for episode_number, looked in episode_list.items():
                if not looked:
                    continue

                user_episodes_data.append(
                    {
                        'id_user': USER_ID,
                        'id_episode': inserted_episodes[
                            f'{tv_show_map[tv_show_name]},{episode_number},{season_number}'
                        ],
                        'looked': True,
                    }
                )

    await db.execute(insert(UserEpisode).values(user_episodes_data))


async def insert_source(db, dump, tv_show_map):
    site_names = {i['site_name'] for i in dump['all_source']}
    inserted_source_info = await db.fetch_all(
        insert(SourceInfo).values([{'site_name': i} for i in site_names]).returning(SourceInfo.id, SourceInfo.site_name)
    )
    source_info_map = {i.site_name: i.id for i in inserted_source_info}

    source_data = []
    for i in dump['all_source']:
        source_data.append(
            {
                'id_tv_show': tv_show_map[i['name']],
                'url': i['url'],
                'id_source_info': source_info_map[i['site_name']],
            }
        )

    await db.execute(insert(Source).values(source_data))


async def insert_tracked_tv_show(db, dump, tv_show_map):
    data = [{'id_user': USER_ID, 'id_tv_show': i} for i in tv_show_map.values()]
    await db.execute(insert(tracked_tv_show_table).values(data))


async def load(db, dump):
    tv_show_map = await insert_tv_show(db, dump)
    await insert_user(db)
    await insert_episode(db, dump, tv_show_map)
    await insert_user_episode(db, dump, tv_show_map)
    await insert_source(db, dump, tv_show_map)
    await insert_tracked_tv_show(db, dump, tv_show_map)


async def main():
    db = await init_db()

    with open('dump.json', encoding='utf8') as inp:
        dump = json.loads(inp.read())

    await load(db, dump)

    await close_db()


if __name__ == '__main__':
    asyncio.run(main())
