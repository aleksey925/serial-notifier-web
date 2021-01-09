def init_routes(app):
    from apps.auth.views import router

    app.include_router(router)
