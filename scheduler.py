import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from structlog import get_logger

from db import init_db, close_db
from logger import init_logger
from updater.update_fetcher import UpdateService

logger = get_logger()
scheduler = AsyncIOScheduler()


async def update_job():
    await UpdateService().start()


list_jobs = [
    {
        'func': update_job,
        'trigger': CronTrigger.from_crontab('*/15 * * * *'),
        'max_instances': 1,
    },
]


async def init_scheduler():
    await init_db()

    for job_args in list_jobs:
        scheduler.add_job(**job_args)

    scheduler.start()
    logger.info('Планировщик периодических задач запущен')


async def shutdown_scheduler():
    logger.info('Завершаем работу планировщика периодических задач')
    scheduler.shutdown(wait=True)
    await close_db()


if __name__ == '__main__':
    init_logger()
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(init_scheduler())
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        loop.run_until_complete(shutdown_scheduler())
