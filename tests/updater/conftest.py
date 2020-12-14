from functools import partial

import pytest
from aioresponses import aioresponses

from updater.update_fetcher import TvShowUpdater

html_files = {
    3: 'filmix_star_trek_discovery.html',
    1: 'filmix_the_walking_dead.html',
    2: 'filmix_flesh.html',
    4: 'seasonvar_flesh.html'
}


@pytest.fixture
async def source_list(db_session):
    return await TvShowUpdater.get_source_list(db_session)


@pytest.yield_fixture
def mocker_source_responses(shared_datadir, source_list):
    def _mocker(resp_mock, count=1):
        for src in source_list:
            html = (
                    shared_datadir / 'tv_show_pages' / html_files[src.id]
            ).read_text()
            for i in range(count):
                resp_mock.get(src.url, status=200, body=html)

    with aioresponses() as responses:
        yield partial(_mocker, resp_mock=responses)
