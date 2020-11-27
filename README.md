serial-notifier-web
===================

Запуск проекта в режиме разработки

```
make run-dev
```

Генерация миграции

```
alembic revision --autogenerate -m "migrate_name"
```

Применение миграций

```
alembic upgrade head
```

Отмена последней миграции

```
alembic downgrade -1
```

Авторизация в gitlab

```
docker login registry.gitlab.com
```

Сборка релизного образа

```
docker build --build-arg CURRENT_ENV=prod -t registry.gitlab.com/alex925/serial-notifier-web:v<X.X.X> .
```

Отправка в репозитрий релизного образа

```
docker push registry.gitlab.com/alex925/serial-notifier-web:v<X.X.X>
```
