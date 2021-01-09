import telebot
from structlog import get_logger

from bot.config import get_config
from bot.handler import init_handler
from bot.logger import init_logger

init_logger()

bot = telebot.TeleBot(token=get_config().TELEGRAM_BOT_TOKEN)
init_handler(bot)

get_logger().info('Бот успешно запущен')
bot.polling()
