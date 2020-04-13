FROM python:3.8.2-alpine3.11

ARG CURRENT_ENV=${CURRENT_ENV}
ENV DOCKERIZE_VERSION=v0.6.1

RUN apk update && \
    apk upgrade && \
    apk add --no-cache git build-base libffi-dev libxslt-dev postgresql-dev &&  \
    wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz && \
    tar -C /usr/local/bin -xzvf dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz && \
    rm dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz

RUN addgroup application \
    && adduser -G application -s /bin/ash -D application

RUN ln -s /usr/bin/python3 /usr/bin/python && \
    ln -s /root/.poetry/bin/poetry /usr/bin/poetry && \
    wget https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py && \
    python3 ./get-poetry.py --version 1.0.5 && \
    poetry config virtualenvs.create false && \
    rm ./get-poetry.py

RUN pip3 install lxml==4.5.0
RUN pip3 install uvloop==0.14.0

COPY pyproject.toml poetry.lock /opt/app/
WORKDIR /opt/app/
RUN /bin/ash -c 'poetry install $(test "$CURRENT_ENV" == prod && echo "--no-dev") --no-interaction --no-ansi'
COPY . /opt/app/
RUN chown -R application:application /opt/app/

USER application
