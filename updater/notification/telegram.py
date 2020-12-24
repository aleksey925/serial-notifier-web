import asyncio
import typing as t
from dataclasses import dataclass

from sqlalchemy import select, and_
from structlog import get_logger
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import get_config
from db import UpdatedTvShow
from models import tracked_tv_show_table, episode_table, Episode, TvShow, TelegramAcc
from updater.notification.base import BaseNotification

logger = get_logger(__name__)


@dataclass
class NotificationData:
    tv_show_id: int
    tv_show_name: str
    id_episode: int
    episode_number: int
    season_number: int
    id_user: int
    chat_id: int


class TelegramNotification(BaseNotification):

    def __init__(self, db_session):
        self._config = get_config()
        self._db_session = db_session

    async def _get_notification_data(self, new_episodes: t.Tuple[UpdatedTvShow, ...]) -> t.Iterable[NotificationData]:
        tracked_tv_show_stmt = (
            select([
                TvShow.id,
                TvShow.name,
                Episode.id.label('id_episode'),
                Episode.episode_number,
                Episode.season_number,
                tracked_tv_show_table.c.id_user,
                TelegramAcc.chat_id,
            ])
            .select_from(
                episode_table
                    .join(TvShow, TvShow.id == Episode.id_tv_show)
                    .join(tracked_tv_show_table, tracked_tv_show_table.c.id_tv_show == episode_table.c.id_tv_show)
                    .join(TelegramAcc, TelegramAcc.id_user == tracked_tv_show_table.c.id_user)
            )
            .where(
                and_(
                    Episode.id.in_(tuple(i.id_episode for i in new_episodes)),
                )
            )
        )
        return (
            NotificationData(
                tv_show_id=i.id,
                tv_show_name=i.name,
                id_episode=i.id_episode,
                episode_number=i.episode_number,
                season_number=i.season_number,
                id_user=i.id_user,
                chat_id=i.chat_id,
            )
            for i in await self._db_session.fetch_all(tracked_tv_show_stmt)
        )

    def _generate_keyboard(self, notif_data: NotificationData):
        callback_data = (
            f'looked {notif_data.id_user},{notif_data.tv_show_id},{notif_data.id_episode},{notif_data.episode_number},'
            f'{notif_data.season_number},'
        )

        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton('Смотрел', callback_data=callback_data + '1'),
            InlineKeyboardButton("Не смотрел", callback_data=callback_data + '0'),
        )
        return keyboard

    def _send(self, notifications: t.Iterable[NotificationData]):
        bot = TeleBot(token=self._config.TELEGRAM_BOT_TOKEN)

        for notif in notifications:
            msg = self._build_notification_msg(notif.tv_show_name, notif.season_number, notif.episode_number)
            try:
                bot.send_message(notif.chat_id, msg, reply_markup=self._generate_keyboard(notif))
            except Exception:
                logger.error(
                    'Возникла ошибка при отправке уведомления через телеграм', msg=msg, chat_id=notif.chat_id
                )

    async def notify(self, new_episodes: t.Tuple[UpdatedTvShow, ...]):
        if not new_episodes:
            return

        logger.info('Начинаем рассылать уведомления через telegram', new_episodes=new_episodes)
        notifications = await self._get_notification_data(new_episodes)
        await asyncio.get_event_loop().run_in_executor(
            None, lambda: self._send(notifications)
        )
