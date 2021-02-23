from fastapi import FastAPI

from apps.auth.routes import init_routes as auth_init_routes
from apps.tv_show.routes import init_routes as tv_show_init_routes
from db import close_db, init_db
from logger import init_logger


def init_events(application):
    application.on_event('startup')(init_db)
    application.on_event('shutdown')(close_db)


def app_factory(app_event=init_events) -> FastAPI:
    init_logger()
    application = FastAPI()
    app_event(application)

    auth_init_routes(application)
    tv_show_init_routes(application)

    return application
