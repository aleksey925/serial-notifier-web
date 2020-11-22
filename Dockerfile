FROM serial-notifier-web:base

ARG CURRENT_ENV=${CURRENT_ENV}

RUN groupadd application \
    && useradd --gid application --shell /bin/bash --create-home application


COPY ./pyproject.toml ./poetry.lock /opt/app/
WORKDIR /opt/app/
RUN /bin/bash -c 'poetry install $(test "$CURRENT_ENV" == prod && echo "--no-dev") --no-interaction --no-ansi'

COPY . /opt/app/


RUN chown -R application:application /opt/app/
USER application
