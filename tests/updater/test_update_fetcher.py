from aioresponses import aioresponses

from db_datacalss import SourceData
from updater.update_fetcher import UpdateFetcher

source_list = [
        SourceData(
            id=2, site_name='filmix', tv_show_name='Сирена',
            url='https://filmix.co/uzhasu/114812-sirena-2016.html',
            encoding=None
        ),
        SourceData(
            id=1, site_name='filmix', tv_show_name='Замок и ключ',
            url='https://filmix.co/drama/139696-zamok-i-klyuch_2020.html',
            encoding=None
        ),
        SourceData(
            id=3, site_name='seasonvar', tv_show_name='Грань',
            url='http://seasonvar.ru/serial-4993-Gran-5-season.html',
            encoding=None
        )
    ]


async def test_downloader__start_download__return_downloaded_pages(
        shared_datadir
):
    list_html_name = [
        'filmix_siren.html', 'filmix_locke_and_key.html',
        'seasonvar_fringe.html'
    ]
    with aioresponses() as responses:
        for src, file_name in zip(source_list, list_html_name):
            html = (shared_datadir / 'tv_show_pages' / file_name).read_text()
            responses.get(src.url, status=200, body=html)

        fetcher = UpdateFetcher(source_list)
        downloaded_pages = await fetcher.start()

    assert downloaded_pages == {
        'filmix': [
            ['Сирена', {'Серия': [1, 2], 'Сезон': 3}],
            ['Замок и ключ', {'Серия': [10], 'Сезон': 1}]
        ],
        'seasonvar': [
            ['Грань', {'Серия': [12, 13], 'Сезон': 5}]
        ]
    }


async def test_downloader__send_empty_source_list__return_empty_dict():
    src_list = []
    with aioresponses() as _:
        fetcher = UpdateFetcher(src_list)
        downloaded_pages = await fetcher.start()

    assert downloaded_pages == {}
