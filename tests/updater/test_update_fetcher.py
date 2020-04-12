from aioresponses import aioresponses

from models import episode
from updater.update_fetcher import (
    UpdateFetcher,
    EpisodesStruct,
    UpdateManager,
)


async def test_downloader__start_download__return_downloaded_pages(
        mocker_source_responses, source_list
):
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


async def test_downloader__send_empty_source_list__return_empty_dict():
    src_list = []
    with aioresponses() as _:
        fetcher = UpdateFetcher(src_list)
        downloaded_pages = await fetcher.start()

    assert downloaded_pages == {}


async def test_update_manager__new_episodes_released__db_updated(
        db_session, mocker_source_responses
):
    mocker_source_responses()
    expect_inserted_episodes = (
        {'id': 333, 'id_tv_show': 3, 'episode_number': 3, 'season_number': 3},
        {'id': 2156, 'id_tv_show': 2, 'episode_number': 15, 'season_number': 6},
        {'id': 11510, 'id_tv_show': 1, 'episode_number': 15, 'season_number': 10}
    )

    list_episode_before = await(
        await db_session.execute(episode.select())
    ).fetchall()

    inserted_episodes = await UpdateManager.start(db_session)

    list_episode_after = await(
        await db_session.execute(episode.select())
    ).fetchall()

    assert len(list_episode_before) == 5
    assert len(list_episode_after) == (
            len(list_episode_before) + len(inserted_episodes)
    )
    assert inserted_episodes == expect_inserted_episodes


async def test_update_manager__not_released_new_episodes__db_not_updated(
        db_session, mocker_source_responses
):
    mocker_source_responses(count=2)
    await UpdateManager.start(db_session)

    list_episode_before = await(
        await db_session.execute(episode.select())
    ).fetchall()

    inserted_episodes = await UpdateManager.start(db_session)

    list_episode_after = await(
        await db_session.execute(episode.select())
    ).fetchall()

    assert inserted_episodes == tuple()
    assert len(list_episode_before) == len(list_episode_after)
