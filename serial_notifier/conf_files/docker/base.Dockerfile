FROM python:3.8.6-buster

ARG CURRENT_ENV=prod
ENV POETRY_VERSION=1.0.5
ENV DOCKERIZE_VERSION=v0.6.1

# Предполагается, что сборка образа будет запускаться из корня проекта
COPY ./libs /opt
WORKDIR /opt/app/
COPY ./serial_notifier/pyproject.toml ./serial_notifier/poetry.lock /opt/app/

RUN apt update \
    && apt-get install -y wget \
    && ln -s /root/.poetry/bin/poetry /usr/bin/poetry \
    && wget https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py \
    && python ./get-poetry.py --version $POETRY_VERSION \
    && poetry config virtualenvs.create false \
    && /bin/bash -c 'poetry install $(test "$CURRENT_ENV" == prod && echo "--no-dev") --no-interaction --no-ansi' \
    && wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm ./get-poetry.py \
    && apt-get purge -y wget \
    && apt autoremove -y \
    && apt autoclean -y \
    && rm -fr /var/lib/apt/lists /var/lib/cache/* /var/log/*
