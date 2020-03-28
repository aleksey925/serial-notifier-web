import json
from copy import copy
from unittest.mock import patch

import pytest

from db import get_user_by_email

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


@patch('auth.business_logic.account.get_token')
async def test_login__send_req_with_valid_data__success(
        get_token_mock, client, db_session
):
    data = json.dumps(VALID_LOGIN_DATA)
    expected = {'token': TOKEN}
    get_token_mock.return_value = TOKEN

    await client.post('/account/registration', data=json.dumps(VALID_REG_DATA))

    resp = await client.post('/account/login', data=data)
    resp_json = json.loads(await resp.text())

    assert resp.status == 200
    assert expected == resp_json


@pytest.mark.parametrize('req_filed', ('email', 'password'))
async def test_login__send_req_without_required_data__return_error(
        client, db_session, req_filed
):
    valid_login_data = copy(VALID_LOGIN_DATA)
    valid_login_data.pop(req_filed)
    data = json.dumps(valid_login_data)

    resp = await client.post('/account/login', data=data)
    resp_json = json.loads(await resp.text())

    assert resp.status == 400
    assert 'VALIDATION_ERROR' == resp_json['code']
    assert req_filed in resp_json['error_fields']


async def test_login__send_email_non_existent_user__return_400(
        client, db_session
):
    data = json.dumps(VALID_LOGIN_DATA)
    expected = {
        'code': 'VALIDATION_ERROR',
        'error_fields': {
            'email': [f'User with email={VALID_LOGIN_DATA["email"]} not exists']
        },
        'message': 'Data is not valid'
    }

    resp = await client.post('/account/login', data=data)
    resp_json = json.loads(await resp.text())

    assert resp.status == 400
    assert expected == resp_json


async def test_registration__send_valid_data__success(client, db_session):
    data = json.dumps(VALID_REG_DATA)
    expected = {'status': 'ok'}

    user_before = await get_user_by_email(db_session, VALID_REG_DATA['email'])

    resp = await client.post('/account/registration', data=data)

    user_after = await get_user_by_email(db_session, VALID_REG_DATA['email'])

    assert resp.status == 200
    assert expected == json.loads(await resp.text())
    assert user_before is None
    assert user_after['email'] == VALID_REG_DATA['email']
    assert user_after['password'] != VALID_REG_DATA['password']


@pytest.mark.parametrize(
    'req_filed', ('sex', 'name', 'surname')
)
async def test_registration__send_req_without_not_required_data__success(
        client, db_session, req_filed
):
    valid_reg_data = copy(VALID_REG_DATA)
    valid_reg_data.pop(req_filed)
    data = json.dumps(valid_reg_data)
    expected = {'status': 'ok'}

    user_before = await get_user_by_email(db_session, VALID_REG_DATA['email'])

    resp = await client.post('/account/registration', data=data)
    resp_json = json.loads(await resp.text())

    user_after = await get_user_by_email(db_session, VALID_REG_DATA['email'])

    assert resp.status == 200
    assert expected == resp_json
    assert user_before is None
    assert user_after[req_filed] is None


@pytest.mark.parametrize(
    'req_filed', ('email', 'password', 'nick')
)
async def test_registration__send_req_without_required_data__return_error(
        client, db_session, req_filed
):
    not_valid_reg_data = copy(VALID_REG_DATA)
    not_valid_reg_data.pop(req_filed)
    data = json.dumps(not_valid_reg_data)

    user_before = await get_user_by_email(db_session, VALID_REG_DATA['email'])

    resp = await client.post('/account/registration', data=data)
    resp_json = json.loads(await resp.text())

    user_after = await get_user_by_email(db_session, VALID_REG_DATA['email'])

    assert resp.status == 400
    assert 'VALIDATION_ERROR' == resp_json['code']
    assert req_filed in resp_json['error_fields']
    assert user_before is None
    assert user_after is None
