async def test_tv_show_all__get_all_tracked_tv_show_with_status__success(
        client, db_session, headers_user1
):
    resp = await client.get('/tv_show/all', headers=headers_user1)
    resp_json = await resp.json()

    assert resp_json == {
        'tv_shows': {
            'Ходячие мертвецы': {'1': [1, 2]},
            'Звездный путь': {'3': [1, 2]}
        }
    }


async def test_tv_show_all__send_request_from_new_user__return_empty(
        client, db_session, headers_user2
):
    resp = await client.get('/tv_show/all', headers=headers_user2)
    resp_json = await resp.json()

    assert resp_json == {'tv_shows': {}}


async def test_tv_show_all__send_req_without_token__return_401(
        client, db_session
):
    resp = await client.get('/tv_show/all')
    resp_json = await resp.json()

    assert resp.status == 401
    assert resp_json == {
        'message': 'Authorization required',
        'code': 'Unauthorized',
        'error_fields': []
    }
