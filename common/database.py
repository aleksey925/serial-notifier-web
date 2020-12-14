import importlib
import json
import logging
import os
from os import path

from alembic.config import main as alembic_commands
from sqlalchemy import create_engine

from common.logger import root_logger_cleaner


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
        logging.getLogger().warning('Возникла ошибка при попытке применить миграции', exc_info=True)
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


def _update_sequence(db_session, auto_inc_cols):
    """
    Обновляет значение sequence на основании которого формируется новое
    значение автоинкреметного поля.
    """
    for table, columns in auto_inc_cols.items():
        _, table_name = table
        for col in columns:
            db_session.execute(
                f"""
                SELECT setval(
                    pg_get_serial_sequence('{table_name}', '{col}'),
                    coalesce(max("{col}"), 1), 
                    max("{col}") IS NOT null
                )
                FROM "{table_name}";"""
            )


def load_data(db_session, base_path, loaded_files):
    """
    Загружает в БД данные из json файлов
    :param db_session: коннект к БД
    :param base_path: путь к папке с файлами содержимое которых нужно загрузить
    в БД
    :param loaded_files: список имен файлов содержимое которых нужно загрузить
    """
    for fixture_file in loaded_files:
        fixture_path = path.join(base_path, fixture_file)
        records = {}
        auto_inc_cols = {}
        for rec in json.loads(open(fixture_path).read()):
            idx_start_table = rec['table'].rfind('.')
            table = (
                rec['table'][:idx_start_table],
                rec['table'][idx_start_table + 1:]
            )

            records.setdefault(table, []).append(rec['fields'])
            auto_inc_cols.setdefault(table, []).extend(
                rec['auto_inc_fields']
            )

        for table, data in records.items():
            module_path, table_name = table
            module_obj = importlib.import_module(module_path)
            # Пакетная загрузка данных
            table_obj = getattr(module_obj, f'{table_name}_table')
            db_session.execute(table_obj.insert(), data)

        _update_sequence(db_session, auto_inc_cols)
