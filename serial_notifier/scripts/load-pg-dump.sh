#!/bin/bash
# Загружает dump созданный pg_dump в локально запущенную БД
set -e
set -x

DESTINATION_HOST=localhost
DESTINATION_PORT=5432
DESTINATION_DATABASE=serial_notifier
DESTINATION_USER=
DESTINATION_PASSWORD=
DESTINATION_CONTAINER=serial-notifier-web_db_1

docker cp $DESTINATION_DATABASE.dump $DESTINATION_CONTAINER:/$DESTINATION_DATABASE.dump
docker exec $DESTINATION_CONTAINER pg_restore -d postgresql://$DESTINATION_USER:$DESTINATION_PASSWORD@$DESTINATION_HOST:$DESTINATION_PORT/$DESTINATION_DATABASE --verbose --clean --create /$DESTINATION_DATABASE.dump
docker exec $DESTINATION_CONTAINER rm /$DESTINATION_DATABASE.dump
