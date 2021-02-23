import pytest

from updater.enums import SupportedSites
from updater.parsers import fanserials, parsers


@pytest.mark.parametrize(
    'file_name, site_name, expected_res',
    (
        ('fanserials_boruto.html', SupportedSites.FANSERIALS.value, {'episodes': [132], 'season': 1}),
        ('fanserials_see.html', SupportedSites.FANSERIALS.value, {'episodes': [4], 'season': 1}),
        ('fanserials_the_purge.html', SupportedSites.FANSERIALS.value, {'episodes': [4], 'season': 2}),
        ('filmix_locke_and_key.html', SupportedSites.FILMIX.value, {'episodes': [10], 'season': 1}),
        ('filmix_siren.html', SupportedSites.FILMIX.value, {'episodes': [1, 2], 'season': 3}),
        ('seasonvar_amazing_stories.html', SupportedSites.SEASONVAR.value, {'episodes': [5], 'season': 1}),
        ('seasonvar_homeland.html', SupportedSites.SEASONVAR.value, {'episodes': [9], 'season': 8}),
        ('seasonvar_fringe.html', SupportedSites.SEASONVAR.value, {'episodes': [12, 13], 'season': 5}),
    ),
)
def test_parsers__get_serial_and_episode__successfully(shared_datadir, file_name, site_name, expected_res):
    html = (shared_datadir / 'tv_show_pages' / file_name).read_text()
    parser_func = parsers[site_name]
    assert parser_func(html) == expected_res


@pytest.mark.parametrize('file_name, expected_res', (('fanserials_the_rookie_without_translate.html', None),))
def test_fanserials__get_episode_without_translate__return_none(shared_datadir, file_name, expected_res):
    html = (shared_datadir / 'tv_show_pages' / file_name).read_text()
    assert fanserials(html) is expected_res
