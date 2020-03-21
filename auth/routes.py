def init_routes(app):
    from auth.views import AccountView

    AccountView.register(app, '/account')
