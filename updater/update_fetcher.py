import asyncio
import logging
import typing
from dataclasses import dataclass

import aiohttp

from db import update_tv_show, get_source_list
from db_datacalss import SourceData
from updater.parsers import parsers

logger = logging.getLogger()


@dataclass
class EpisodesStruct:
    id_tv_show: int
    episode_info: typing.Optional[dict]


class UpdateFetcher:

    def __init__(self, source_list: typing.List[SourceData]):
        super().__init__()
        self._source_list = source_list

    async def _fetch(
            self,
            session,
            store: dict,
            site_name: str,
            id_tv_show: int,
            url: str,
            encoding: typing.Optional[str]
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
            logger.error(f'URL {kwargs["url"]} имеет неправильный формат')
        except aiohttp.ClientConnectionError:
            logger.error(f'Невозможно установить соединение с {kwargs["url"]}')
        except Exception:
            logger.exception(
                f'Возникла непредвиденная ошибка при подключении к '
                f'{kwargs["url"]}'
            )

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

    async def start(self) -> typing.Dict[str, typing.List[EpisodesStruct]]:
        fetched_episodes = {}
        await self._wrapper_for_tasks(fetched_episodes)
        return fetched_episodes


class UpdateManager:

    def prepare_data_before_insert(
            self,
            fetched_episodes: typing.Dict[str, typing.List[EpisodesStruct]]
    ) -> typing.List[dict]:
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

    async def start(self, db_session) -> typing.Tuple[dict, ...]:
        source_list = await get_source_list(db_session)
        fetcher = UpdateFetcher(source_list)
        fetched_episodes = await fetcher.start()
        inserted_episodes = await update_tv_show(
            db_session, self.prepare_data_before_insert(fetched_episodes)
        )
        return inserted_episodes
