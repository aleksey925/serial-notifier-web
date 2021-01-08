from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from auth.security import get_current_user
from common.exceptions import ObjectDoesNotExist
from common.schemas import ErrorResp
from models import User
from tv_show.schemas import TvShowSchema, UserEpisodeReqSchema, UserEpisodeRespSchema
from tv_show.service import TvShowService

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
