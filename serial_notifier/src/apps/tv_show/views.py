from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from serial_notifier_schema.tv_show import TvShowSchema, UserEpisodeReqSchema, UserEpisodeRespSchema

from apps.auth.security import get_current_user
from apps.common.exceptions import ObjectDoesNotExist
from apps.common.schemas import ErrorResp
from apps.tv_show.service import TvShowService
from models import User

router = APIRouter()


@router.get('/tv_show/', response_model=TvShowSchema)
async def get_all_user_tv_show(user: User = Depends(get_current_user)):
    user_tv_show = await TvShowService().get_all_user_tv_show(user.id)
    return {'tv_shows': user_tv_show}


@router.post(
    '/tv_show/episode/{id_episode}/', response_model=UserEpisodeRespSchema, responses={400: {"model": ErrorResp}}
)
async def update_user_episode(user_episode: UserEpisodeReqSchema, user: User = Depends(get_current_user)):
    try:
        updated_user_episode = await TvShowService().update_user_episode(id_user=user.id, usr_episode=user_episode)
        return updated_user_episode.dict()
    except ObjectDoesNotExist as exc:
        return JSONResponse(content={'detail': str(exc)}, status_code=400)
