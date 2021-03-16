import telebot
import urllib3.exceptions
from structlog import get_logger

from bot.config import get_config
from bot.handler import init_handler
from bot.logger import init_logger
from bot.utils import retry

init_logger()

bot = telebot.TeleBot(token=get_config().TELEGRAM_BOT_TOKEN)
init_handler(bot)

get_logger().info('Начинаем прослушивать события от telegram')
retry(bot.polling, exception=urllib3.exceptions.ReadTimeoutError)
