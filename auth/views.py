from aiohttp import web

from muffin_classy import AIOHttpView, route

from common.rest_api.error import error_handler
from common.validate import validate_payload
from auth.business_logic.account import registration, login
from auth.schemas import LoginSchema, RegistrationSchema


class AccountView(AIOHttpView):

    @error_handler
    @validate_payload(LoginSchema())
    @route(methods=['POST'])
    async def login(self, request, payload: dict):
        token = await login(request['db_session'], payload)
        return web.json_response({'token': token})

    @error_handler
    @validate_payload(RegistrationSchema())
    @route(methods=['POST'])
    async def registration(self, request, payload: dict):
        await registration(request['db_session'], payload)
        return web.json_response({'status': 'ok'})
