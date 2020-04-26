import typing

from db import get_user_tv_show

AllTvShowType = typing.Dict[str, typing.Dict[int, typing.List[int]]]


async def get_all_user_tv_show(db_session, user_id: int) -> AllTvShowType:
    """
    Извлекает из БД информацию о всех сериалах отслеживаемых пользователем.
    :param db_session: подключение к БД
    :param user_id: идентификатор пользователя
    :return: словарь с сериалами. Пример возвращаемых данных:
    {'Звездный путь': {3: [1, 2]}, 'Ходячие мертвецы': {1: [1, 2]}}
    """
    user_tv_show = await get_user_tv_show(db_session, user_id)

    all_tv_show = {}
    for rec in user_tv_show:
        tv_show_data = all_tv_show.setdefault(rec['name'], {})
        tv_show_data.setdefault(rec['season_number'], []).append(
            rec['episode_number']
        )

    return all_tv_show
