def init_routes(app):
    from apps.tv_show.views import router

    app.include_router(router)
