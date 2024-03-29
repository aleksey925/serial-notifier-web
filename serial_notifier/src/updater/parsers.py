import re
from typing import Dict, List, Optional, Union

import lxml.html
from structlog import get_logger

from updater.enums import SupportedSites

logger = get_logger(__name__)


def seasonvar(page: str) -> Optional[Dict[str, Union[int, List[int]]]]:
    parser = lxml.html.fromstring(page)

    try:
        last_season_row_elem = parser.cssselect('ul.tabs-result > li > h2:last-child a')[0]
    except IndexError:
        logger.warning('На сайте seasonvar не удалось найти блок хранящий информацию о последней серии')
        return

    extracted_season = re.findall(r'(\d+) сезон', last_season_row_elem.text)
    season = int(extracted_season[0]) if extracted_season else 1

    try:
        episodes_raw = last_season_row_elem.cssselect('span')[0].text
        extracted_episodes = re.findall(
            r'(\d+-{0,1}\d*) серия.*\)',
            episodes_raw,
        )[0]
    except IndexError:
        logger.warning('Не удалось извлечь информацию о сериях')
        return

    if '-' in extracted_episodes:
        episodes = list(range(*list(map(int, extracted_episodes.split('-')))))
        episodes.append(episodes[-1] + 1)
    else:
        episodes = [int(extracted_episodes)]

    return {'episodes': episodes, 'season': season}


def filmix(page: str) -> Optional[Dict[str, Union[int, List[int]]]]:
    parser = lxml.html.fromstring(page)

    try:
        data = parser.cssselect('.added-info')[0].text
    except IndexError:
        logger.warning('На сайте filmix не удалсь найти блок хранящий информацию о ' 'последней серии')
        return

    episodes = re.findall(r'([\d-]+) серия', data, re.IGNORECASE)
    season = re.findall(r'([\d-]+) сезон', data, re.IGNORECASE)

    if not episodes:
        logger.warning('Не удалось извлечь информацию о сериях')
        return

    season = int(season[0]) if season else 1

    if episodes[0].find('-') != -1:
        episodes = list(range(*list(map(int, episodes[0].split('-')))))
        episodes.append(episodes[-1] + 1)
    else:
        episodes = [int(episodes[0])]

    return {'episodes': episodes, 'season': season}


def fanserials(page: str) -> Optional[Dict[str, Union[int, List[int]]]]:
    parser = lxml.html.fromstring(page)

    try:
        last_episode_elem = parser.cssselect('#episode_list li')[0]
    except IndexError:
        logger.warning('На сайте fanserials не удалось найти блок хранящий информацию о последней серии')
        return

    try:
        episode_info = last_episode_elem.cssselect('.field-description a')[0].text
    except IndexError:
        logger.warning('Не удалось извлечь информацию о сериях')
        return

    translate_info = tuple(i.text.lower() for i in last_episode_elem.cssselect('.serial-translate span a'))

    if len(translate_info) == 1 and 'оригинал' in translate_info:
        return

    extracted_episode = re.findall(r'([\d-]+) серия', episode_info, re.I)
    extracted_season = re.findall(r'([\d-]+) сезон', episode_info, re.I)

    episodes = list(map(int, extracted_episode))
    season = int(extracted_season[0]) if extracted_season else 1

    return {'episodes': episodes, 'season': season}


parsers = {
    SupportedSites.SEASONVAR.value: seasonvar,
    SupportedSites.FILMIX.value: filmix,
    SupportedSites.FANSERIALS.value: fanserials,
}
