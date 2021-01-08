from unittest.mock import Mock, patch, call

import pytest

from bot.handler import notification_button_click_handler

ID_USER = 1
ID_TV_SHOW = 2
ID_EPISODE = 123
EPISODE_NUMBER = 1
SEASON_NUMBER = 1


class TestNotificationButtonClickHandler:

    @pytest.fixture
    def callback_id(self):
        return '362235236344'

    @pytest.fixture
    def looked_episode_data(self):
        return f'looked {ID_USER},{ID_TV_SHOW},{ID_EPISODE},{EPISODE_NUMBER},{SEASON_NUMBER},1'

    @pytest.fixture
    def not_looked_episode_data(self):
        return f'looked {ID_USER},{ID_TV_SHOW},{ID_EPISODE},{EPISODE_NUMBER},{SEASON_NUMBER},0'

    @pytest.fixture
    def looked_episode_not_valid_data(self):
        return f'looked {ID_USER},{ID_EPISODE},{EPISODE_NUMBER},{SEASON_NUMBER},1'

    @pytest.fixture
    def bot_mock(self):
        return Mock()

    @pytest.fixture
    def callback_query_mock(self, callback_id, looked_episode_data):
        mock = Mock()
        mock.id = callback_id
        mock.data = looked_episode_data
        return mock

    @pytest.mark.parametrize('is_looked, resp_text', [(True, 'Смотрел'), (False, 'Не смотрел')])
    @patch('requests.session')
    def test_handle_valid_data__success(
            self, session_mock, bot_mock, callback_query_mock, looked_episode_data, not_looked_episode_data,
            callback_id, is_looked, resp_text
    ):
        callback_data = {True: looked_episode_data, False: not_looked_episode_data}
        session_mock_inst = session_mock()
        callback_query_mock.data = callback_data[is_looked]

        notification_button_click_handler(bot_mock, callback_query_mock)

        assert session_mock_inst.post.call_args == call(
            url=f'http://127.0.0.1:8080/tv_show/episode/{ID_EPISODE}/',
            json={'id_episode': ID_EPISODE, 'looked': is_looked}
        )
        assert bot_mock.answer_callback_query.call_args == call(callback_id, resp_text)

    @patch('bot.handler.Client')
    def test_handle_not_valid_data__error_handled(
            self, client_mock, bot_mock, callback_query_mock, looked_episode_not_valid_data, callback_id
    ):
        callback_query_mock.data = looked_episode_not_valid_data
        client_mock_inst = client_mock()

        notification_button_click_handler(bot_mock, callback_query_mock)

        assert client_mock_inst.update_user_episode.call_count == 0
        assert bot_mock.answer_callback_query.call_args == call(callback_id, 'Не удалось обработать данные кнопки')
