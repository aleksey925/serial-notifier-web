def init_routes(app):
    from tv_show.views import TvShowView

    TvShowView.register(app, '/tv_show')
