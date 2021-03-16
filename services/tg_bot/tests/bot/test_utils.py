from unittest.mock import patch

import pytest

from bot.exception import RetryNumberAttemptsExceededException
from bot.utils import retry


class TelebotMock:
    def __init__(self):
        self.count = 5

    def __call__(self, *args, **kwargs):
        while self.count:
            self.count -= 1
            raise Exception()

        return 'connect'


def connect_to_telegram_mock():
    raise Exception()


@patch('time.sleep')
def test_retry__call_class_inst_wait_success_resp__success(time_sleep_mock):
    time_sleep_mock.sleep = lambda *args, **kwargs: print('sleep', args, kwargs)

    result = retry(TelebotMock())

    assert result == 'connect'


@patch('time.sleep')
def test_retry__call_func_wait_success_resp__raise_error(time_sleep_mock):
    time_sleep_mock.sleep = lambda *args, **kwargs: print('sleep', args, kwargs)

    with pytest.raises(RetryNumberAttemptsExceededException):
        retry(connect_to_telegram_mock)
