import pytest
from asynctest import patch

from updater.notification.telegram import NotificationData, TelegramNotification
from updater.update_fetcher import TvShowUpdater


@pytest.mark.asyncio
class TestTelegramNotification:
    @pytest.fixture
    async def new_episodes(self, db_session):
        episodes = (
            {'id_tv_show': 1, 'episode_number': 3, 'season_number': 1},
            {'id_tv_show': 3, 'episode_number': 3, 'season_number': 3},
            {'id_tv_show': 3, 'episode_number': 4, 'season_number': 3},
            {'id_tv_show': 4, 'episode_number': 1, 'season_number': 1},
            {'id_tv_show': 5, 'episode_number': 1, 'season_number': 4},
        )
        return await TvShowUpdater(db_session).update_tv_show(episodes)

    async def test_get_notification_data(self, db_session, new_episodes):
        updated_tv_show = {f'{ep.id_tv_show},{ep.episode_number},{ep.season_number}': ep for ep in new_episodes}

        notifications = await TelegramNotification(db_session)._get_notification_data(new_episodes)

        assert tuple(notifications) == (
            NotificationData(
                tv_show_id=3,
                tv_show_name='Звездный путь',
                id_episode=updated_tv_show['3,3,3'].id_episode,
                episode_number=3,
                season_number=3,
                id_user=1,
                chat_id=564346,
            ),
            NotificationData(
                tv_show_id=3,
                tv_show_name='Звездный путь',
                id_episode=updated_tv_show['3,4,3'].id_episode,
                episode_number=4,
                season_number=3,
                id_user=1,
                chat_id=564346,
            ),
            NotificationData(
                tv_show_id=1,
                tv_show_name='Ходячие мертвецы',
                id_episode=updated_tv_show['1,3,1'].id_episode,
                episode_number=3,
                season_number=1,
                id_user=1,
                chat_id=564346,
            ),
            NotificationData(
                tv_show_id=3,
                tv_show_name='Звездный путь',
                id_episode=updated_tv_show['3,3,3'].id_episode,
                episode_number=3,
                season_number=3,
                id_user=3,
                chat_id=444356,
            ),
            NotificationData(
                tv_show_id=3,
                tv_show_name='Звездный путь',
                id_episode=updated_tv_show['3,4,3'].id_episode,
                episode_number=4,
                season_number=3,
                id_user=3,
                chat_id=444356,
            ),
        )

    @patch('updater.notification.telegram.TeleBot')
    async def test_notify(self, telebot_mock, db_session, new_episodes):
        telebot_inst_mock = telebot_mock()

        await TelegramNotification(db_session).notify(new_episodes)

        assert tuple(i[0] for i in telebot_inst_mock.send_message.call_args_list) == (
            (564346, 'Звездный путь: Сезон 3, Серия 3'),
            (564346, 'Звездный путь: Сезон 3, Серия 4'),
            (564346, 'Ходячие мертвецы: Сезон 1, Серия 3'),
            (444356, 'Звездный путь: Сезон 3, Серия 3'),
            (444356, 'Звездный путь: Сезон 3, Серия 4'),
        )

    async def test_generate_keyboard(self):
        looked_callback_data = {
            'user_id': 1,
            'tv_show_id': 3,
            'id_episode': 45,
            'episode_number': 3,
            'season_number': 3,
            'looked': True,
        }
        not_looked_callback_data = looked_callback_data.copy()
        not_looked_callback_data['looked'] = False
        notif_data = NotificationData(
            tv_show_id=looked_callback_data['tv_show_id'],
            tv_show_name='Звездный путь',
            id_episode=looked_callback_data['id_episode'],
            episode_number=looked_callback_data['episode_number'],
            season_number=looked_callback_data['season_number'],
            id_user=looked_callback_data['user_id'],
            chat_id=564346,
        )

        keyboard = TelegramNotification(None)._generate_keyboard(notif_data)
        looked, not_looked = keyboard.keyboard[0]

        assert looked.text == 'Смотрел'
        assert looked.callback_data == 'looked 1,3,45,3,3,1'
        assert not_looked.text == 'Не смотрел'
        assert not_looked.callback_data == 'looked 1,3,45,3,3,0'
