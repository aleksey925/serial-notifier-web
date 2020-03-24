def init_routes(app):
    from tv_show.views import UserTvShowView

    UserTvShowView.register(app, '/user_tv_show')
