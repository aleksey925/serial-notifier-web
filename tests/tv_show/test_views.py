import pytest


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
