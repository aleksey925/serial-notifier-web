FROM registry.gitlab.com/alex925/serial-notifier-web/app:base

ARG CURRENT_ENV=${CURRENT_ENV}

RUN groupadd application \
    && useradd --gid application --shell /bin/bash --create-home application


# Предполагается, что сборка образа будет запускаться из корня проекта
COPY ./libs /opt/libs
COPY ./serial_notifier/pyproject.toml ./serial_notifier/poetry.lock /opt/app/
WORKDIR /opt/app/
RUN /bin/bash -c 'poetry install $(test "$CURRENT_ENV" == prod && echo "--no-dev") --no-interaction --no-ansi'

COPY ./serial_notifier /opt/app/

RUN chown -R application:application /opt/app/
USER application
