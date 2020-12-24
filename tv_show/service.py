import typing as t

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from db import get_db
from models import episode_table, tv_show_table, user_table, tracked_tv_show_table, user_episode_table, UserEpisode
from tv_show.schemas import UserEpisodeReqSchema, UserEpisodeRespSchema


class TvShowService:

    def __init__(self):
        self.db = get_db()

    async def _get_tv_show(self, user_id: int) -> t.Tuple[dict, ...]:
        all_tv_show_stmt = select([
            tv_show_table.c.name,
            episode_table.c.id.label('episode_id'),
            episode_table.c.season_number,
            episode_table.c.episode_number
        ]).where(
            user_table.c.id == user_id
        ).select_from(
            user_table.join(
                tracked_tv_show_table,
                tracked_tv_show_table.c.id_user == user_table.c.id
            ).join(
                tv_show_table,
                tv_show_table.c.id == tracked_tv_show_table.c.id_tv_show
            ).join(
                episode_table, episode_table.c.id_tv_show == tv_show_table.c.id
            )
        ).cte('all_tv_show')

        looked_episodes_stmt = select([
            episode_table.c.id.label('episode_id'),
            user_episode_table.c.looked
        ]).where(
            user_table.c.id == user_id
        ).select_from(
            user_table.join(
                user_episode_table,
                user_episode_table.c.id_user == user_table.c.id
            ).join(
                episode_table,
                episode_table.c.id == user_episode_table.c.id_episode
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

    async def update_user_episode(self, usr_episode: UserEpisodeReqSchema) -> UserEpisodeRespSchema:
        """
        Выполняет обновление информации об эпизоде
        :param usr_episode: изменения, которые необходимо зафиксировать в БД
        :return: обновленная информация об эпизоде
        """
        inserted_data = usr_episode.dict()
        updated_usr_episode = await self.db.fetch_one(
            insert(user_episode_table)
            .values(**inserted_data)
            .on_conflict_do_update(
                constraint='constraint_unique_episode_for_user',
                set_={'looked': inserted_data['looked']}
            )
            .returning(
                UserEpisode.id,
                UserEpisode.id_user,
                UserEpisode.id_episode,
                UserEpisode.looked,
            )
        )

        return UserEpisodeRespSchema(**dict(updated_usr_episode))
