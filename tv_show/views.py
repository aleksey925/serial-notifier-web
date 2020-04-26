from aiohttp import web
from aiohttp_jwt import login_required

from muffin_classy import AIOHttpView

from common.rest_api.error import error_handler
from tv_show.business_logic.tv_show import get_all_user_tv_show
from tv_show.schemas import TvShow

tv_show_schema = TvShow()


class TvShowView(AIOHttpView):

    @error_handler
    @login_required
    async def all(self, request):
        user_id = request['user']['user_id']
        user_tv_show = await get_all_user_tv_show(
            request['db_session'], user_id
        )
        return web.json_response(
            {'tv_shows': user_tv_show},
            dumps=lambda i: tv_show_schema.dumps(i)
        )
