import pytest

from updater.enumerations import SupportedSites
from updater.parsers import fanserials, parsers


@pytest.mark.parametrize(
    'file_name, site_name, expected_res', (
            ('fanserials_boruto.html', SupportedSites.FANSERIALS.value, {'Серия': [132], 'Сезон': 1}),
            ('fanserials_see.html', SupportedSites.FANSERIALS.value, {'Серия': [4], 'Сезон': 1}),
            ('fanserials_the_purge.html', SupportedSites.FANSERIALS.value, {'Серия': [4], 'Сезон': 2}),
            ('filmix_locke_and_key.html', SupportedSites.FILMIX.value, {'Серия': [10], 'Сезон': 1}),
            ('filmix_siren.html', SupportedSites.FILMIX.value, {'Серия': [1, 2], 'Сезон': 3}),
            ('seasonvar_amazing_stories.html', SupportedSites.SEASONVAR.value, {'Серия': [5], 'Сезон': 1}),
            ('seasonvar_homeland.html', SupportedSites.SEASONVAR.value, {'Серия': [9], 'Сезон': 8}),
            ('seasonvar_fringe.html', SupportedSites.SEASONVAR.value, {'Серия': [12, 13], 'Сезон': 5}),
    )
)
def test_parsers__get_serial_and_episode__successfully(
    shared_datadir, file_name, site_name, expected_res
):
    html = (shared_datadir / 'tv_show_pages' / file_name).read_text()
    parser_func = parsers[site_name]
    assert parser_func(html) == expected_res


@pytest.mark.parametrize(
    'file_name, expected_res', (
            ('fanserials_the_rookie_without_translate.html', None),
    )
)
def test_fanserials__get_episode_without_translate__return_none(
        shared_datadir, file_name, expected_res
):
    html = (shared_datadir / 'tv_show_pages' / file_name).read_text()
    assert fanserials(html) is expected_res
