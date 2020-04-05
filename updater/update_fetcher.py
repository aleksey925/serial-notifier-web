import asyncio
import logging
import typing

import aiohttp

from db_datacalss import SourceData
from updater.parsers import parsers

logger = logging.getLogger()


class UpdateFetcher:

    def __init__(self, source_list: typing.List[SourceData]):
        super().__init__()
        self._source_list = source_list

    async def _fetch(
            self,
            session,
            store: dict,
            site_name: str,
            tv_show_name: str,
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
                [tv_show_name, parsers[site_name](page)]
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
                        tv_show_name=source.tv_show_name,
                        url=source.url,
                        encoding=source.encoding
                    )
                )

            if not tasks:
                logger.debug('Нет сериалов для отслежвания')
                return

            await asyncio.gather(*tasks)

    async def start(self) -> dict:
        new_episodes = {}
        await self._wrapper_for_tasks(new_episodes)
        return new_episodes
