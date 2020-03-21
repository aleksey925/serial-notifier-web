import logging
import os

from alembic.config import main as alembic_commands
from sqlalchemy import create_engine

from tests.utils.logger import root_logger_cleaner


def apply_migrations(root_dir):
    """
    Применяет к текущей БД все миграции
    :param root_dir: корневая дирректория проекта (дирректория в которой
    располагается папка alembic, содержащая миграции)
    """
    cwd = os.getcwd()
    os.chdir(root_dir)
    logger_cleaner = root_logger_cleaner()
    next(logger_cleaner)

    try:
        alembic_commands(argv=('--raiseerr', 'upgrade', 'head',))
    except Exception as err:
        next(logger_cleaner)
        logging.getLogger('serial-notifier').error(
            f'Возникла ошибка при попытке применить миграции: {err}'
        )
        raise
    finally:
        os.chdir(cwd)

    next(logger_cleaner)


def create_db(default_db_uri, db_name):
    engine = create_engine(default_db_uri, isolation_level='AUTOCOMMIT')

    with engine.connect() as conn:
        drop_db(default_db_uri, db_name)
        conn.execute(f'CREATE DATABASE {db_name}')


def drop_db(default_db_uri, db_name):
    engine = create_engine(default_db_uri, isolation_level='AUTOCOMMIT')

    with engine.connect() as conn:
        # terminate all connections to be able to drop database
        conn.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{db_name}'
                AND pid <> pg_backend_pid();""")
        conn.execute(f'DROP DATABASE IF EXISTS {db_name}')
