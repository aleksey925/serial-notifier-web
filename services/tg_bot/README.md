tg-bot
======

tg-bot - телеграм бот для взаимодействия с сервисом serial-notifier-web.


### Создание релиза

Сборка образа

```
docker build --build-arg CURRENT_ENV=prod -t registry.gitlab.com/alex925/serial-notifier-web/tg-bot:v<X.X.X> .
```

Отправка образа в private registry

```
docker push registry.gitlab.com/alex925/serial-notifier-web/tg-bot:v<X.X.X>
```
