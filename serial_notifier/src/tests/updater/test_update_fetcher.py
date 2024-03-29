import copy

import pytest
from aioresponses import aioresponses

from db import UpdatedTvShow
from models import Episode
from updater.update_fetcher import EpisodesStruct, TvShowMemoryStorage, TvShowUpdater, UpdateFetcher


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
        'seasonvar': [EpisodesStruct(2, {'episodes': [15], 'season': 6})],
    }


@pytest.mark.asyncio
async def test_downloader__send_empty_source_list__return_empty_dict():
    src_list = []
    with aioresponses() as _:
        fetcher = UpdateFetcher(src_list)
        downloaded_pages = await fetcher.start()

    assert downloaded_pages == {}


@pytest.mark.asyncio
class TestTvShowMemoryStorage:
    async def test_find_new_episode(self, db_session):
        fetched_episodes = {
            'filmix': [
                EpisodesStruct(3, {'episodes': [1, 2, 3], 'season': 3}),
                EpisodesStruct(2, {'episodes': [4, 5, 6], 'season': 6}),
                EpisodesStruct(1, {'episodes': [15], 'season': 1}),
            ],
            'seasonvar': [
                EpisodesStruct(1, {'episodes': [1], 'season': 10}),
                EpisodesStruct(2, {'episodes': [5], 'season': 6}),
            ],
        }

        storage = TvShowMemoryStorage(db_session)
        all_tv_show_before = copy.deepcopy(await storage.get_all_tv_show())
        new_episodes = await storage.find_new_episode(fetched_episodes)
        all_tv_show_after = await storage.get_all_tv_show()

        assert new_episodes == [
            {'id_tv_show': 3, 'episode_number': 3, 'season_number': 3},
            {'id_tv_show': 2, 'episode_number': 5, 'season_number': 6},
            {'id_tv_show': 2, 'episode_number': 6, 'season_number': 6},
            {'id_tv_show': 1, 'episode_number': 15, 'season_number': 1},
            {'id_tv_show': 1, 'episode_number': 1, 'season_number': 10},
        ]
        assert all_tv_show_before == {1: {1: {1, 2}}, 3: {3: {1, 2}}, 2: {6: {4}}}
        assert all_tv_show_after == {1: {1: {1, 2, 15}, 10: {1}}, 3: {3: {1, 2, 3}}, 2: {6: {4, 5, 6}}}


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

        inserted_episodes = await TvShowUpdater(db_session).start()

        count_episode_after = await db_session.query(Episode).count()

        assert count_episode_before == 5
        assert count_episode_after == (count_episode_before + len(inserted_episodes))
        assert inserted_episodes == expect_inserted_episodes

    async def test_start__not_released_new_episodes__db_not_updated(self, db_session, mocker_source_responses):
        mocker_source_responses(count=2)
        await TvShowUpdater(db_session).start()

        count_episode_before = await db_session.query(Episode).count()

        inserted_episodes = await TvShowUpdater(db_session).start()

        count_episode_after = await db_session.query(Episode).count()

        assert inserted_episodes == tuple()
        assert count_episode_before == count_episode_after
