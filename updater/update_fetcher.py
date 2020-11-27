import asyncio
import logging
import typing as t
from dataclasses import dataclass

import aiohttp
from sqlalchemy.dialects.postgresql import insert

from db import get_source_list, SourceData, UpdatedTvShow
from models import episode
from updater.notification.telegram import TelegramNotification
from updater.parsers import parsers

logger = logging.getLogger(__name__)


@dataclass
class EpisodesStruct:
    id_tv_show: int
    episode_info: t.Optional[dict]


class UpdateFetcher:

    def __init__(self, source_list: t.List[SourceData]):
        super().__init__()
        self._source_list = source_list

    async def _fetch(
            self,
            session,
            store: dict,
            site_name: str,
            id_tv_show: int,
            url: str,
            encoding: t.Optional[str]
    ):
        async with session.get(url, allow_redirects=True) as resp:
            if resp.status != 200:
                logger.error(
                    f'При загрузке страницы {url} возникли проблемы, http '
                    f'код: {resp.status}'
                )
                return

            page = await resp.text(encoding=encoding)
            store[site_name].append(
                EpisodesStruct(id_tv_show, parsers[site_name](page))
            )

    async def _fetch_wrapper(self, semaphore, **kwargs):
        try:
            async with semaphore:
                await self._fetch(**kwargs)
        except ValueError:
            logger.error(f'URL {kwargs["url"]} имеет неправильный формат', exc_info=True)
        except aiohttp.ClientConnectionError:
            logger.error(f'Невозможно установить соединение с {kwargs["url"]}')
        except Exception:
            logger.exception(f'Возникла непредвиденная ошибка при подключении к {kwargs["url"]}')

    async def _wrapper_for_tasks(self, store: dict):
        tasks = []

        semaphore = asyncio.Semaphore(1000)
        connector = aiohttp.TCPConnector(verify_ssl=False)
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
                        encoding=source.encoding
                    )
                )

            if not tasks:
                logger.debug('Нет сериалов для отслежвания')
                return

            await asyncio.gather(*tasks)

    async def start(self) -> t.Dict[str, t.List[EpisodesStruct]]:
        fetched_episodes = {}
        await self._wrapper_for_tasks(fetched_episodes)
        return fetched_episodes


class TvShowUpdater:

    @staticmethod
    async def update_tv_show(conn, fetched_episodes: t.List[dict]) -> t.Tuple[UpdatedTvShow, ...]:
        if not fetched_episodes:
            return tuple()

        stmt = (
            insert(episode)
            .values(fetched_episodes)
            .on_conflict_do_nothing()
            .returning(
                episode.c.id, episode.c.id_tv_show, episode.c.episode_number, episode.c.season_number
            )
        )
        return tuple(
            UpdatedTvShow(
                id_episode=i['id'],
                id_tv_show=i['id_tv_show'],
                episode_number=i['episode_number'],
                season_number=i['season_number']
            ) for i in await (await conn.execute(stmt)).fetchall()
        )

    @staticmethod
    def prepare_data_before_insert(fetched_episodes: t.Dict[str, t.List[EpisodesStruct]]) -> t.List[dict]:
        prepared_data = []

        for site_name, episodes in fetched_episodes.items():
            for ep in episodes:
                if not ep.episode_info:
                    continue

                for episode_number in ep.episode_info['episodes']:
                    prepared_data.append({
                        'id': int(
                            str(ep.id_tv_show) + str(episode_number) +
                            str(ep.episode_info['season'])
                        ),
                        'id_tv_show': ep.id_tv_show,
                        'episode_number': episode_number,
                        'season_number': ep.episode_info['season'],
                    })

        return prepared_data

    @classmethod
    async def start(cls, db_session) -> t.Tuple[UpdatedTvShow, ...]:
        logger.info('Запущено обновление')
        source_list = await get_source_list(db_session)
        fetcher = UpdateFetcher(source_list)
        fetched_episodes = await fetcher.start()
        inserted_episodes = await cls.update_tv_show(
            db_session, cls.prepare_data_before_insert(fetched_episodes)
        )
        logger.info(
            f'В БД была добавлена информация о {len(inserted_episodes)} новых '
            f'сериях'
        )
        logger.info('Обновление завершено')
        return inserted_episodes


class UpdateService:

    def __init__(self, db_session):
        self._db_session = db_session

    async def start(self):
        inserted_episodes = await TvShowUpdater.start(self._db_session)
        await TelegramNotification(db_session=self._db_session).notify(new_episodes=inserted_episodes)
