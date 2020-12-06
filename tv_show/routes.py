def init_routes(app):
    from tv_show.views import router

    app.include_router(router)
