tg-bot
======

tg-bot - телеграм бот для взаимодействия с сервисом serial-notifier.


- [Production](#Production)
    - [Деплой](#Деплой)


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
    docker build --build-arg CURRENT_ENV=prod -t registry.gitlab.com/alex925/serial-notifier-web/tg-bot:v2.0.0 .
    docker push registry.gitlab.com/alex925/serial-notifier-web/tg-bot:v2.0.0
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
    docker pull registry.gitlab.com/alex925/serial-notifier-web/tg-bot:v<X.X.X>
    ```

- В переменной `PROD_IMAGE_TAG` объявленной в `.env` файле прописываем версию сервиса, которую мы хотим 
  запустить `v<X.X.X>`

- Обновляем контейнеры

    ```
    make run
    ```
