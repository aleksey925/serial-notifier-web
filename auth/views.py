from fastapi import APIRouter, HTTPException, status

from auth.exceptions import LoginException, UserAlreadyExists
from auth.schemas import LoginReqSchema, TokenRespSchema, RegistrationReqSchema, RegistrationRespSchema
from auth.service import AccountService

router = APIRouter()


@router.post('/auth/token/', response_model=TokenRespSchema)
async def get_token(payload: LoginReqSchema):
    try:
        token = await AccountService().login(payload)
    except LoginException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authorization error. Check the login and password.',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    return {'access_token': token, 'token_type': 'bearer'}


@router.post('/user/', response_model=RegistrationRespSchema)
async def reg_new_user(payload: RegistrationReqSchema):
    try:
        new_user = await AccountService().registration(payload)
    except UserAlreadyExists as exc:
        raise HTTPException(
            status_code=422,
            detail=[
                {
                    'loc': ['body', exc.not_unique_field],
                    'msg': 'Not unique value',
                    'type': 'value_error.not_unique',
                }
            ]
        )

    return new_user
