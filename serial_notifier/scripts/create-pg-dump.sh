#!/bin/bash
# Создает dump БД при помощи pg_dump
set -e
set -x

SOURCE_HOST=127.0.0.1
SOURCE_PORT=5432
SOURCE_DATABASE=serial_notifier
SOURCE_USER=
SOURCE_PASSWORD=
SOURCE_CONTAINER=serial-notifier-web_db_1

DUMP_COMMAND="pg_dump -Fc postgresql://$SOURCE_USER:$SOURCE_PASSWORD@$SOURCE_HOST:$SOURCE_PORT/$SOURCE_DATABASE"

docker exec $SOURCE_CONTAINER $DUMP_COMMAND > "${SOURCE_DATABASE}.dump"
