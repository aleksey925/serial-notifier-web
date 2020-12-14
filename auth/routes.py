def init_routes(app):
    from auth.views import router

    app.include_router(router)
