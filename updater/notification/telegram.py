import asyncio
import logging
import typing as t
from dataclasses import dataclass

from sqlalchemy import select, and_
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import get_config
from db import UpdatedTvShow
from models import telegram_acc, tracked_tv_show, tv_show, episode
from updater.notification.base import BaseNotification

logger = logging.getLogger(__name__)


@dataclass
class NotificationData:
    tv_show_id: int
    tv_show_name: str
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
                tv_show.c.id,
                tv_show.c.name,
                episode.c.episode_number,
                episode.c.season_number,
                tracked_tv_show.c.id_user,
                telegram_acc.c.chat_id,
            ])
            .select_from(
                episode
                    .join(tv_show, tv_show.c.id == episode.c.id_tv_show)
                    .join(tracked_tv_show, tracked_tv_show.c.id_tv_show == episode.c.id_tv_show)
                    .join(telegram_acc, telegram_acc.c.id_user == tracked_tv_show.c.id_user)
            )
            .where(
                and_(
                    episode.c.id.in_(tuple(i.id_episode for i in new_episodes)),
                )
            )
        )
        res = await self._db_session.execute(tracked_tv_show_stmt)
        return (
            NotificationData(
                tv_show_id=i.id,
                tv_show_name=i.name,
                episode_number=i.episode_number,
                season_number=i.season_number,
                id_user=i.id_user,
                chat_id=i.chat_id,
            )
            for i in await res.fetchall()
        )

    def _generate_keyboard(self, notif_data: NotificationData):
        callback_data = (
            f'looked {notif_data.id_user},{notif_data.tv_show_id},{notif_data.episode_number},'
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
                    f'Возникла ошибка при отправке уведомления через телеграм msg={msg} chat_id={notif.chat_id}'
                )

    async def notify(self, new_episodes: t.Tuple[UpdatedTvShow, ...]):
        notifications = await self._get_notification_data(new_episodes)
        await asyncio.get_event_loop().run_in_executor(
            None, lambda: self._send(notifications)
        )
