import json

import pytest

from models import UserEpisode


@pytest.mark.asyncio
async def test_tv_show_all__get_all_tracked_tv_show_with_status__success(async_client, db_session, headers_user1):
    resp = await async_client.get('/tv_show/all/', headers=headers_user1)
    resp_json = resp.json()

    assert resp_json == {
        'tv_shows': {
            'Ходячие мертвецы': {'1': [1, 2]},
            'Звездный путь': {'3': [1, 2]}
        }
    }


@pytest.mark.asyncio
async def test_tv_show_all__send_request_from_new_user__return_empty(async_client, db_session, headers_user2):
    resp = await async_client.get('/tv_show/all/', headers=headers_user2)
    resp_json = resp.json()

    assert resp_json == {'tv_shows': {}}


@pytest.mark.asyncio
async def test_tv_show_all__send_req_without_token__return_401(async_client, db_session):
    resp = await async_client.get('/tv_show/all/')
    resp_json = resp.json()

    assert resp.status_code == 401
    assert resp_json == {'detail': 'Not authenticated'}


@pytest.mark.asyncio
class TestUpdateUserEpisode:

    async def test_create_new_record__success(self, async_client, db_session, headers_user1):
        data = {
            'id_user': 1,
            'id_episode': 121,
            'looked': True,
        }
        usr_episode_before = await db_session.query(UserEpisode).filter_by(
            id_user=data['id_user'],
            id_episode=data['id_episode'],
        ).one_or_none()

        resp = await async_client.post(
            f'/tv_show/episode/{data["id_episode"]}/',
            data=json.dumps(data),
            headers=headers_user1,
        )
        resp_data = resp.json()

        usr_episode_after = await db_session.query(UserEpisode).filter_by(
            id_user=data['id_user'],
            id_episode=data['id_episode'],
        ).one_or_none()

        assert resp.status_code == 200
        assert usr_episode_before is None
        assert usr_episode_after.id == resp_data['id']
        assert resp_data == {
            'id': resp_data['id'],
            'id_user': 1,
            'id_episode': data['id_episode'],
            'looked': data['looked'],
        }

    async def test_update_record__success(self, async_client, db_session, headers_user1):
        data = {
            'id_user': 1,
            'id_episode': 111,
            'looked': False,
        }
        usr_episode_before = await db_session.query(UserEpisode).filter_by(
            id_user=data['id_user'],
            id_episode=data['id_episode'],
        ).one()

        resp = await async_client.post(
            f'/tv_show/episode/{data["id_episode"]}/',
            data=json.dumps(data),
            headers=headers_user1,
        )
        resp_data = resp.json()

        usr_episode_after = await db_session.query(UserEpisode).filter_by(
            id_user=data['id_user'],
            id_episode=data['id_episode'],
        ).one()

        assert resp.status_code == 200
        assert usr_episode_before.looked is True
        assert usr_episode_after.looked is False
        assert resp_data == {
            'id': usr_episode_before.id,
            'id_user': data['id_user'],
            'id_episode': data['id_episode'],
            'looked': data['looked'],
        }

    async def test_send_not_auth_request__return401(self, async_client, db_session):
        data = {
            'id_user': 1,
            'id_episode': 111,
            'looked': False,
        }
        usr_episode_before = await db_session.query(UserEpisode).filter_by(
            id_user=data['id_user'],
            id_episode=data['id_episode'],
        ).one()

        resp = await async_client.post(
            f'/tv_show/episode/{data["id_episode"]}/',
            data=json.dumps(data),
        )
        resp_data = resp.json()

        usr_episode_after = await db_session.query(UserEpisode).filter_by(
            id_user=data['id_user'],
            id_episode=data['id_episode'],
        ).one()

        assert resp.status_code == 401
        assert resp_data == {'detail': 'Not authenticated'}
        assert usr_episode_before.looked is True
        assert usr_episode_after.looked is True
        assert usr_episode_after.looked != data['looked']
