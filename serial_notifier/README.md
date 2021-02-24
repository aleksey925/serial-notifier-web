serial-notifier
===============

serial-notifier - backend приложения для отслеживания появления новых серий у сериалов.


# Содержание

- [Разработка](#Разработка)

    - [Настройка dev окружения](#Настройка-dev-окружения)
    - [Работа с миграциями](#Работа-с-миграциями)
    - [Сборка docker образа](#Сборка-docker-образа)
      
- [Production](#Production)
    - [Деплой](#Деплой)
    


## Разработка

<a name='Настройка-dev-окружения'></a>
### Настройка dev окружения

1. Авторизуемся в gitlab

    ```
    docker login registry.gitlab.com
    ```

2. Создаем `.env` по примеру `.env.example`

3. Выполняем сборку docker образа

    ```
    make build-dev-app-img
    ```

4. Устанавливаем зависимости сервиса для того, чтобы можно было вне docker запускать линтеры, тесты и т д

    ```
    poetry install
    ```

5. Запускаем сервис в docker

    ```
    make run-dev
    ```


<a name='Работа-с-миграциями'></a>
### Работа с миграциями

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


<a name='Сборка-docker-образа'></a>
### Сборка docker образа

- Сборка базового docker образа

    ```
    make build-base-img
    ```
    
    Может пригодиться, если в private registry еще не попал обновленный образ или при доработке сервиса был обновлен 
    base.Dockerfile и нужно получить актуальный образ.

- Сборка dev docker образа

    ```
    build-dev-app-img
    ```
    
    Может пригодится, если были обновлены зависимости проекта или просто был обновлен Dockerfile.



<a name='Production'></a>
### Production


<a name='Деплой'></a>
### Деплой

**Создание релиза**

В инструкции находящиеся ниже предполагается, что

- создается релиз с версией `v2.0.0`
- в прод идут изменения из ветки master
- изменения при разработке мержились в develop и теперь эти изменения нужно вынести на прод

1. Переходим на текущую версию master и создаем tag, ссылающийся на нее (это необходимо делать, если создается первый 
релиз) 
    
    ```
    git tag v1.0.0
    ```
   
2. Переключаемся на актуальный develop и заменяем master содержимым ветки develop

    ```
    git push --force origin HEAD:master
    ```

3. Переходим в master и создаем tag с новой версией сервиса

    ```
    git tag v2.0.0
    ```
   
4. Пушим созданные теги

    ```
    git push origin v1.0.0 v2.0.0
    ```

5. Собираем docker образ и отправляем его private registry (необходимо выполнять его этот этап не делается в pipeline)

    ```
    docker build --build-arg CURRENT_ENV=prod -t registry.gitlab.com/alex925/serial-notifier-web/app:v2.0.0 .
    docker push registry.gitlab.com/alex925/serial-notifier-web/app:v2.0.0
    ```

**Деплой релиза на стенд**

В инструкции находящиеся ниже предполагается, что `v<X.X.X>` будет заменено на устанавливаемую версию приложения.


Деплой приложения и воркеров:

- Получаем из git все новые ветки и теги

    ```
    git fetch --all --tags
    ```

- Загружаем содержимое тега
    
    ``` 
    git reset --hard v<X.X.X>
    ```

- Получаем свежий docker образ с приложением

    ```
    docker pull registry.gitlab.com/alex925/serial-notifier-web/app:v<X.X.X>
    ```

- В переменной `PROD_IMAGE_TAG` объявленной в `.env` файле прописываем версию сервиса, которую мы хотим 
  запустить `v<X.X.X>`

- Обновляем контейнеры

    ```
    make run
    ```