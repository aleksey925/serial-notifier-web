async def test_tv_show_all__get_all_tracked_tv_show_with_status__success(
        client, db_session, headers_user1
):
    resp = await client.get('/tv_show/all', headers=headers_user1)
    resp_json = await resp.json()

    assert resp_json == [
        {
            "name": "Ходячие мертвецы",
            "season_number": 1,
            "looked": True,
            "episode_number": 1
        },
        {
            "name": "Ходячие мертвецы",
            "season_number": 1,
            "looked": False,
            "episode_number": 2
        },
        {
            "name": "Звездный путь",
            "season_number": 3,
            "looked": True,
            "episode_number": 1
        },
        {
            "name": "Звездный путь",
            "season_number": 3,
            "looked": False,
            "episode_number": 2
        }
    ]


async def test_tv_show_all__send_request_from_new_user__return_empty(
        client, db_session, headers_user2
):
    resp = await client.get('/tv_show/all', headers=headers_user2)
    resp_json = await resp.json()

    assert resp_json == []


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
