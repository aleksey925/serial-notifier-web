from aiohttp import web
from aiohttp_jwt import login_required

from muffin_classy import AIOHttpView

from common.rest_api.error import error_handler
from tv_show.business_logic.tv_show import get_all_user_tv_show


class UserTvShowView(AIOHttpView):

    @error_handler
    @login_required
    async def all(self, request):
        # TODO Покрыть тестами
        user_id = request['user']['user_id']
        json_user_tv_show = await get_all_user_tv_show(
            request['db_session'], user_id
        )
        return web.json_response(text=json_user_tv_show)
