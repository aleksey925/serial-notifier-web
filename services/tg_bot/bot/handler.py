from functools import partial

from serial_notifier_api.api import Client
from serial_notifier_schema.tv_show import UserEpisodeReqSchema
from structlog import get_logger
from telebot import TeleBot
from telebot.types import CallbackQuery

from bot.config import get_config
from bot.utils import parse_looked_button_data

logger = get_logger(__name__)
config = get_config()


def init_handler(bot: TeleBot):
    bot.message_handler(commands=['start'])(partial(start_message_handler, bot=bot))
    bot.callback_query_handler(func=lambda call: call.data.startswith('looked'))(
        partial(notification_button_click_handler, bot=bot)
    )


def start_message_handler(message, *, bot: TeleBot):
    bot.send_message(
        message.chat.id,
        'Привет! К сожалению, я пока мало, что умею и не могу тебя зарегистрировать. Регистрация будет сделана позже.',
    )


def notification_button_click_handler(call: CallbackQuery, *, bot: TeleBot):
    """
    Обрабатывает клики по кнопкам "Смотрел", "Не смотрел"
    :param call: объект содержащий информацию об обрабатываемом событии
    :param bot: экземпляр запущенного бота
    """
    try:
        button_data = parse_looked_button_data(call.data)
    except Exception:
        bot.answer_callback_query(call.id, 'Не удалось обработать данные кнопки')
        logger.warn('Не удалось обработать данные кнопки', data=call.data, exc_info=True)
        return

    client_api = Client(
        base_url=config.API_BASE_URL,
        user_id=button_data.id_user,
        jwt_secret=config.JWT_SECRET,
        jwt_exp_delta_min=config.JWT_EXP_DELTA_MIN,
        jwt_algorithm=config.JWT_ALGORITHM,
    )
    try:
        client_api.update_user_episode(UserEpisodeReqSchema(**button_data.dict()))
    except Exception:
        bot.answer_callback_query(call.id, 'Не удалось обновить информацию о выбранном эпизоде')
        logger.warn('Не удалось обновить информацию о выбранном эпизоде', exc_info=True)
        return

    if button_data.looked:
        bot.answer_callback_query(call.id, 'Смотрел')
    else:
        bot.answer_callback_query(call.id, 'Не смотрел')
