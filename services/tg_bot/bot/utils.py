import time
import typing as t

from structlog import get_logger
from telebot.types import InlineKeyboardMarkup

from bot.exception import RetryNumberAttemptsExceededException
from bot.schema import LookedButtonData

logger = get_logger()


def parse_looked_button_data(raw_data: str) -> LookedButtonData:
    return LookedButtonData(*raw_data.replace('looked ', '').split(','))


def clear_keyboard_button(keyboard_markup: InlineKeyboardMarkup, emoji: str) -> InlineKeyboardMarkup:
    if emoji:
        for row in keyboard_markup.keyboard:
            for button in row:
                button.text = button.text.replace(emoji, '')

    return keyboard_markup


def highlight_selected_button(keyboard_markup: InlineKeyboardMarkup, text_button: str, emoji: str):
    """
    Добавляет перед текстом кнопки emoji, который отражает какое действие было выполнено.
    :param keyboard_markup: разметка клавиатуры
    :param text_button: текст нажатой кнопки
    :param emoji: смайлик добавляемый перед текстом кнопки
    :return: обновленная разметка клавиатуры
    """
    keyboard_markup = clear_keyboard_button(keyboard_markup, emoji)
    for row in keyboard_markup.keyboard:
        for button in row:
            if button.text == text_button:
                button.text = f'{emoji} {button.text}'

    return keyboard_markup


def retry(fn: t.Callable, count: int = 10, sleep: int = 2, exception=Exception):
    while count:
        try:
            return fn()
        except exception:
            logger.info(
                'Возникла ошибка, пытаемся выполнить перезапуск...',
                fn=fn.__class__.__name__,
                count=count,
                exc_info=True,
            )
            count -= 1
            time.sleep(sleep)

    logger.error('Не удалось выполнить перезапуск', fn=fn.__name__, count=count, exc_info=True)
    raise RetryNumberAttemptsExceededException()
