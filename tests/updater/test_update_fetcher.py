import pytest
from aioresponses import aioresponses

from db import UpdatedTvShow
from models import Episode
from updater.update_fetcher import (
    UpdateFetcher,
    EpisodesStruct,
    TvShowUpdater,
)


@pytest.mark.asyncio
async def test_downloader__start_download__return_downloaded_pages(mocker_source_responses, source_list):
    mocker_source_responses()
    fetcher = UpdateFetcher(source_list)
    downloaded_pages = await fetcher.start()

    assert downloaded_pages == {
        'filmix': [
            EpisodesStruct(3, {'episodes': [3], 'season': 3}),
            EpisodesStruct(2, {'episodes': [15], 'season': 6}),
            EpisodesStruct(1, {'episodes': [15], 'season': 10}),
        ],
        'seasonvar': [
            EpisodesStruct(2, {'episodes': [15], 'season': 6})
        ]
    }


@pytest.mark.asyncio
async def test_downloader__send_empty_source_list__return_empty_dict():
    src_list = []
    with aioresponses() as _:
        fetcher = UpdateFetcher(src_list)
        downloaded_pages = await fetcher.start()

    assert downloaded_pages == {}


@pytest.mark.asyncio
class TestTvShowUpdater:

    async def test_start__new_episodes_released__db_updated(self, db_session, mocker_source_responses):
        mocker_source_responses()
        expect_inserted_episodes = (
            UpdatedTvShow(**{'id_episode': 1, 'id_tv_show': 3, 'episode_number': 3, 'season_number': 3}),
            UpdatedTvShow(**{'id_episode': 2, 'id_tv_show': 2, 'episode_number': 15, 'season_number': 6}),
            UpdatedTvShow(**{'id_episode': 3, 'id_tv_show': 1, 'episode_number': 15, 'season_number': 10}),
        )
        count_episode_before = await db_session.query(Episode).count()

        inserted_episodes = await TvShowUpdater.start(db_session)

        count_episode_after = await db_session.query(Episode).count()

        assert count_episode_before == 5
        assert count_episode_after == (count_episode_before + len(inserted_episodes))
        assert inserted_episodes == expect_inserted_episodes

    async def test_start__not_released_new_episodes__db_not_updated(self, db_session, mocker_source_responses):
        mocker_source_responses(count=2)
        await TvShowUpdater.start(db_session)

        count_episode_before = await db_session.query(Episode).count()

        inserted_episodes = await TvShowUpdater.start(db_session)

        count_episode_after = await db_session.query(Episode).count()

        assert inserted_episodes == tuple()
        assert count_episode_before == count_episode_after
