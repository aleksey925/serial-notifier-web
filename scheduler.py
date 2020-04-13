from functools import partial
from multiprocessing import Value

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from updater.update_fetcher import UpdateManager

_is_started = Value('b', False)


async def update_job(app):
    async with app['db'].acquire() as db_session:
        await UpdateManager.start(db_session)


list_jobs = [
    {
        'func': update_job,
        'trigger': CronTrigger.from_crontab('*/15 * * * *'),
        'max_instances': 1,
    },
]


async def init_scheduler(app):
    if _is_started.value:
        return

    scheduler = AsyncIOScheduler()
    app['scheduler'] = scheduler

    for job_args in list_jobs:
        func = job_args.pop('func')
        func_name = func.__name__
        func = partial(func, app=app)
        func.__name__ = func_name
        scheduler.add_job(func=func, **job_args)

    scheduler.start()
    _is_started.value = True

    return scheduler


async def shutdown_scheduler(app):
    app['scheduler'].shutdown(wait=True)
