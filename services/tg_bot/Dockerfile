FROM registry.gitlab.com/alex925/serial-notifier-web/tg-bot:base

ARG CURRENT_ENV=${CURRENT_ENV}

RUN groupadd application \
    && useradd --gid application --shell /bin/bash --create-home application


# Предполагается, что сборка образа будет запускаться из корня проекта
COPY ./libs /opt
COPY ./services/tg_bot/pyproject.toml ./services/tg_bot/poetry.lock /opt/app/
WORKDIR /opt/app/
RUN /bin/bash -c 'poetry install $(test "$CURRENT_ENV" == prod && echo "--no-dev") --no-interaction --no-ansi'

COPY . /opt/app/

RUN chown -R application:application /opt/app/
USER application
