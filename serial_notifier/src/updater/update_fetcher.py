import asyncio
import typing as t
from dataclasses import dataclass

import aiohttp
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from structlog import get_logger

from db import UpdatedTvShow, get_db
from models import Episode, episode_table, source_info_table, source_table
from updater.notification.telegram import TelegramNotification
from updater.parsers import parsers

logger = get_logger(__name__)


@dataclass
class EpisodesStruct:
    id_tv_show: int
    episode_info: t.Optional[dict]


@dataclass
class SourceData:
    id: int  # noqa: A003
    id_tv_show: int
    site_name: str
    url: str
    encoding: t.Optional[str] = None


class UpdateFetcher:
    def __init__(self, source_list: t.List[SourceData]):
        super().__init__()
        self._source_list = source_list

    async def _fetch(self, session, store: dict, site_name: str, id_tv_show: int, url: str, encoding: t.Optional[str]):
        async with session.get(url, allow_redirects=True) as resp:
            if resp.status != 200:
                logger.warn('При загрузке страницы возникли проблемы,', url=url, status_code=resp.status)
                return

            page = await resp.text(encoding=encoding)
            store[site_name].append(EpisodesStruct(id_tv_show, parsers[site_name](page)))

    async def _fetch_wrapper(self, semaphore, **kwargs):
        try:
            async with semaphore:
                await self._fetch(**kwargs)
        except ValueError:
            logger.warn(f'URL {kwargs["url"]} имеет неправильный формат', exc_info=True)
        except aiohttp.ClientConnectionError:
            logger.warn('Невозможно установить соединение', url=kwargs["url"])
        except Exception:
            logger.warn('Возникла непредвиденная ошибка при подключении', url=kwargs["url"], exc_info=True)

    async def _wrapper_for_tasks(self, store: dict):
        tasks = []

        semaphore = asyncio.Semaphore(1000)
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            for source in self._source_list:
                store[source.site_name] = []
                tasks.append(
                    self._fetch_wrapper(
                        semaphore=semaphore,
                        session=session,
                        store=store,
                        site_name=source.site_name,
                        id_tv_show=source.id_tv_show,
                        url=source.url,
                        encoding=source.encoding,
                    )
                )

            if not tasks:
                logger.debug('Нет сериалов для отслеживания')
                return

            await asyncio.gather(*tasks)

    async def start(self) -> t.Dict[str, t.List[EpisodesStruct]]:
        fetched_episodes = {}
        await self._wrapper_for_tasks(fetched_episodes)
        return fetched_episodes


class TvShowMemoryStorage(object):

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, db_session):
        self.db_session = db_session
        self.storage: t.Dict[int : t.Dict[int, set]] = {}

    async def get_all_tv_show(self):
        if self.storage:
            return self.storage

        all_tv_show_stmt = select([Episode.id_tv_show, Episode.episode_number, Episode.season_number])

        for episode_data in await self.db_session.fetch_all(all_tv_show_stmt):
            tv_show_info = self.storage.setdefault(episode_data['id_tv_show'], {})
            season_info = tv_show_info.setdefault(episode_data['season_number'], set())
            season_info.add(episode_data['episode_number'])

        return self.storage

    def update_tv_show(self, id_tv_show: int, season_number: int, episodes: t.Iterable[int]):
        self._update_tv_show(self.storage, id_tv_show, season_number, episodes)

    def _update_tv_show(self, target_storage: dict, id_tv_show: int, season_number: int, episodes: t.Iterable[int]):
        new_tv_show = target_storage.setdefault(id_tv_show, {})
        new_season = new_tv_show.setdefault(season_number, set())
        new_season.update(episodes)

    async def find_new_episode(self, fetched_episodes: t.Dict[str, t.List[EpisodesStruct]]) -> t.List[dict]:
        await self.get_all_tv_show()

        all_updated_episodes = []
        for site_name, list_episodes_struct in fetched_episodes.items():
            for episode_inf in list_episodes_struct:
                stored_tv_show = self.storage.get(episode_inf.id_tv_show)
                if not stored_tv_show:
                    for i in episode_inf.episode_info['episodes']:
                        all_updated_episodes.append(
                            {
                                'id_tv_show': episode_inf.id_tv_show,
                                'episode_number': i,
                                'season_number': episode_inf.episode_info['season'],
                            }
                        )
                    self._update_tv_show(
                        self.storage,
                        episode_inf.id_tv_show,
                        episode_inf.episode_info['season'],
                        episode_inf.episode_info['episodes'],
                    )
                    continue

                stored_episodes = stored_tv_show.get(episode_inf.episode_info['season'], set())
                new_episodes = set(episode_inf.episode_info['episodes']) - stored_episodes
                if new_episodes:
                    for i in new_episodes:
                        all_updated_episodes.append(
                            {
                                'id_tv_show': episode_inf.id_tv_show,
                                'episode_number': i,
                                'season_number': episode_inf.episode_info['season'],
                            }
                        )
                    self._update_tv_show(
                        self.storage, episode_inf.id_tv_show, episode_inf.episode_info['season'], new_episodes
                    )

        return all_updated_episodes


class TvShowUpdater:
    def __init__(self, db_session):
        self.db_session = db_session

    @staticmethod
    async def get_source_list(conn) -> t.List[SourceData]:
        source_stmt = select(
            [
                source_table.c.id,
                source_table.c.id_tv_show,
                source_info_table.c.site_name,
                source_table.c.url,
                source_info_table.c.encoding,
            ]
        ).select_from(source_table.join(source_info_table, source_info_table.c.id == source_table.c.id_source_info))
        return [SourceData(**src) for src in await conn.fetch_all(source_stmt)]

    async def update_tv_show(self, fetched_episodes: t.List[dict]) -> t.Tuple[UpdatedTvShow, ...]:
        if not fetched_episodes:
            return tuple()

        stmt = (
            insert(episode_table)
            .values(fetched_episodes)
            .on_conflict_do_nothing()
            .returning(
                episode_table.c.id,
                episode_table.c.id_tv_show,
                episode_table.c.episode_number,
                episode_table.c.season_number,
            )
        )
        return tuple(
            UpdatedTvShow(
                id_episode=i['id'],
                id_tv_show=i['id_tv_show'],
                episode_number=i['episode_number'],
                season_number=i['season_number'],
            )
            for i in await self.db_session.fetch_all(stmt)
        )

    async def start(self) -> t.Tuple[UpdatedTvShow, ...]:
        logger.info('Запущено обновление')
        source_list = await self.get_source_list(self.db_session)
        fetcher = UpdateFetcher(source_list)
        fetched_episodes = await fetcher.start()
        new_episodes = await TvShowMemoryStorage(self.db_session).find_new_episode(fetched_episodes)
        inserted_episodes = await self.update_tv_show(new_episodes)
        logger.info('В БД была добавлена информация о новых сериях', count_episode=len(inserted_episodes))
        logger.info('Обновление завершено')
        return inserted_episodes


class UpdateService:
    def __init__(self):
        self._db_session = get_db()

    async def start(self):
        inserted_episodes = await TvShowUpdater(self._db_session).start()
        await TelegramNotification(db_session=self._db_session).notify(new_episodes=inserted_episodes)


if __name__ == '__main__':
    from db import init_db

    async def run():
        await init_db()
        await UpdateService().start()

    asyncio.run(run())
