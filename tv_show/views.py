from fastapi import APIRouter, Depends

from auth.security import get_current_user
from models import User
from tv_show.schemas import TvShowSchema
from tv_show.service import TvShowService

router = APIRouter()


@router.get('/tv_show/all/', response_model=TvShowSchema)
async def get_all_user_tv_show(user: User = Depends(get_current_user)):
    user_tv_show = await TvShowService().get_all_user_tv_show(user.id)
    return {'tv_shows': user_tv_show}
