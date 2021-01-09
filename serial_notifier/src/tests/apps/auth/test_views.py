import json
from copy import copy

import pytest
from asynctest import patch
from fastapi import Depends

from apps.auth.security import get_current_user, create_access_token
from config import get_config
from models import User

VALID_LOGIN_DATA = {
    'email': 'dima@ya.ru',
    'password': '123'
}

VALID_REG_DATA = {
    'email': 'dima@ya.ru',
    'password': '123',
    'sex': 'male',
    'nick': 'dima',
    'name': 'Дима',
    'surname': 'Иванов',
}

TOKEN = (
    'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE1ODQ'
    '4MDUxMzJ9.oMU-K6sdjuFJUfiosWYFeNhYbS5i2fpDG_iUbQ5r97c'
)


@pytest.mark.asyncio
class TestAuth:

    @pytest.yield_fixture
    def private_view(self, app):

        @app.get('/test-view/')
        def test_view(user: User = Depends(get_current_user)):
            return {'status': 'ok'}

        yield test_view

    @patch('apps.auth.service.create_access_token')
    async def test_get_token__send_req_with_valid_data__success(
            self, create_access_token_mock, async_client, db_session
    ):
        expected = {'access_token': TOKEN, 'token_type': 'bearer'}
        create_access_token_mock.return_value = TOKEN

        await async_client.post('/user/', data=json.dumps(VALID_REG_DATA))

        resp = await async_client.post('/auth/token/', data=json.dumps(VALID_LOGIN_DATA))
        resp_json = resp.json()

        assert resp.status_code == 200
        assert expected == resp_json

    @pytest.mark.parametrize('req_filed', ('email', 'password'))
    async def test_get_token__send_req_without_required_data__return_error(self, async_client, db_session, req_filed):
        valid_login_data = copy(VALID_LOGIN_DATA)
        valid_login_data.pop(req_filed)
        data = json.dumps(valid_login_data)

        resp = await async_client.post('/auth/token/', data=data)
        resp_json = resp.json()

        assert resp.status_code == 422
        assert resp_json['detail'][0]['loc'] == ['body', req_filed]
        assert resp_json['detail'][0]['msg'] == 'field required'
        assert len(resp_json['detail']) == 1

    async def test_get_token__send_email_non_existent_user__return_401(self, async_client, db_session):
        resp = await async_client.post('/auth/token/', data=json.dumps(VALID_LOGIN_DATA))
        resp_json = resp.json()

        assert resp.status_code == 401
        assert resp_json == {'detail': 'Authorization error. Check the login and password.'}

    async def test_get_current_user__get_non_existed_user_id__return_401(self, private_view, async_client):
        token = create_access_token({'user_id': 99999}, get_config().JWT_SECRET)

        resp = await async_client.get('/test-view/', headers={'Authorization': f'Bearer {token}'})
        resp_json = resp.json()

        assert resp.status_code == 401
        assert resp_json == {'detail': 'Could not validate credentials'}


@pytest.mark.asyncio
async def test_registration__send_valid_data__success(async_client, db_session):
    expected = VALID_REG_DATA.copy()
    del expected['password']

    user_before = await db_session.query(User).filter(User.email == VALID_REG_DATA['email']).one_or_none()

    resp = await async_client.post('/user/', data=json.dumps(VALID_REG_DATA))

    user_after = await db_session.query(User).filter(User.email == VALID_REG_DATA['email']).one()
    expected['id'] = user_after.id

    assert resp.status_code == 200
    assert expected == resp.json()
    assert user_before is None
    assert user_after.email == VALID_REG_DATA['email']
    assert user_after.password != VALID_REG_DATA['password']


@pytest.mark.asyncio
async def test_registration__send_data_existed_user__return_validation_error(async_client, db_session):
    reg_data = copy(VALID_REG_DATA)
    reg_data['email'] = 'test@ya.ru'
    expected = {
        'detail': [
            {
                'loc': ['body', 'email'],
                'msg': 'Not unique value',
                'type': 'value_error.not_unique'
            }
        ]
    }

    resp = await async_client.post('/user/', data=json.dumps(reg_data))

    assert resp.status_code == 422
    assert resp.json() == expected


@pytest.mark.parametrize('req_filed', ('sex', 'name', 'surname'))
@pytest.mark.asyncio
async def test_registration__send_req_without_not_required_data__success(async_client, db_session, req_filed):
    valid_reg_data = copy(VALID_REG_DATA)
    valid_reg_data.pop(req_filed)
    expected_resp = {
        'email': 'dima@ya.ru',
        'name': 'Дима',
        'nick': 'dima',
        'sex': 'male',
        'surname': 'Иванов'
    }
    expected_resp[req_filed] = None

    user_before = await db_session.query(User).filter(User.email == VALID_REG_DATA['email']).one_or_none()

    resp = await async_client.post('/user/', data=json.dumps(valid_reg_data))
    resp_json = resp.json()

    user_after = await db_session.query(User).filter(User.email == VALID_REG_DATA['email']).one()
    expected_resp['id'] = user_after.id

    assert resp.status_code == 200
    assert expected_resp == resp_json
    assert user_before is None
    assert getattr(user_after, req_filed) is None


@pytest.mark.parametrize('req_filed', ('email', 'password', 'nick'))
@pytest.mark.asyncio
async def test_registration__send_req_without_required_data__return_error(async_client, db_session, req_filed):
    not_valid_reg_data = copy(VALID_REG_DATA)
    not_valid_reg_data.pop(req_filed)
    expected_resp = {'detail': [{'loc': ['body', req_filed], 'msg': 'field required', 'type': 'value_error.missing'}]}

    user_before = await db_session.query(User).filter(User.email == VALID_REG_DATA['email']).one_or_none()

    resp = await async_client.post('/user/', data=json.dumps(not_valid_reg_data))
    resp_json = resp.json()

    user_after = await db_session.query(User).filter(User.email == VALID_REG_DATA['email']).one_or_none()

    assert resp.status_code == 422
    assert resp_json == expected_resp
    assert user_before is None
    assert user_after is None
