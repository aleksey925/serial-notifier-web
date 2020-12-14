import typing as t

from sqlalchemy import select

from db import get_db
from models import episode, tv_show, user_table, tracked_tv_show, user_episode


class TvShowService:

    def __init__(self):
        self.db = get_db()

    async def _get_tv_show(self, user_id: int) -> t.Tuple[dict, ...]:
        all_tv_show_stmt = select([
            tv_show.c.name,
            episode.c.id.label('episode_id'),
            episode.c.season_number,
            episode.c.episode_number
        ]).where(
            user_table.c.id == user_id
        ).select_from(
            user_table.join(
                tracked_tv_show,
                tracked_tv_show.c.id_user == user_table.c.id
            ).join(
                tv_show,
                tv_show.c.id == tracked_tv_show.c.id_tv_show
            ).join(
                episode, episode.c.id_tv_show == tv_show.c.id
            )
        ).cte('all_tv_show')

        looked_episodes_stmt = select([
            episode.c.id.label('episode_id'),
            user_episode.c.looked
        ]).where(
            user_table.c.id == user_id
        ).select_from(
            user_table.join(
                user_episode,
                user_episode.c.id_user == user_table.c.id
            ).join(
                episode,
                episode.c.id == user_episode.c.id_episode
            )
        ).cte('looked_episodes')

        res = await self.db.fetch_all(
            select([
                all_tv_show_stmt.c.name,
                all_tv_show_stmt.c.season_number,
                all_tv_show_stmt.c.episode_number,
                looked_episodes_stmt.c.looked
            ]).select_from(
                all_tv_show_stmt.outerjoin(
                    looked_episodes_stmt,
                    all_tv_show_stmt.c.episode_id == looked_episodes_stmt.c.episode_id
                )
            )
        )
        return tuple(dict(i) for i in res)

    async def get_all_user_tv_show(self, user_id: int) -> t.Dict[str, t.Dict[int, t.List[int]]]:
        """
        Извлекает из БД информацию о всех сериалах отслеживаемых пользователем.
        :param user_id: идентификатор пользователя
        :return: словарь с сериалами.
        Пример возвращаемых данных:
        {'Звездный путь': {3: [1, 2]}, 'Ходячие мертвецы': {1: [1, 2]}}
        """
        user_tv_show = await self._get_tv_show(user_id)

        all_tv_show = {}
        for rec in user_tv_show:
            tv_show_data = all_tv_show.setdefault(rec['name'], {})
            tv_show_data.setdefault(rec['season_number'], []).append(rec['episode_number'])

        return all_tv_show
