import asyncio
import json

from sqlalchemy import select

from apps.tv_show.service import TvShowService
from config import get_config
from db import init_db, close_db
from models import SourceInfo, Source, TvShow

USER_ID = 1

conf = get_config()


async def get_source(db):
    a = select([
        SourceInfo.site_name,
        Source.url,
        TvShow.name,
    ]).select_from(
        Source.__table__.join(
            SourceInfo,
            Source.id_source_info == SourceInfo.id
        ).join(
            TvShow,
            Source.id_tv_show == TvShow.id
        )
    )
    return tuple(dict(i) for i in await db.fetch_all(a))


async def main():
    db = await init_db()

    service = TvShowService()
    all_tv_show = await service.get_all_user_tv_show(user_id=USER_ID)
    all_source = await get_source(db)

    await close_db()

    with open('dump.json', 'w', encoding='utf8') as out:
        out.write(
            json.dumps(
                {
                    'all_tv_show': all_tv_show,
                    'all_source': all_source,
                },
                indent=3,
                ensure_ascii=False,
            )
        )


if __name__ == '__main__':
    asyncio.run(main())
