from bot.schema import LookedButtonData


def parse_looked_button_data(raw_data: str) -> LookedButtonData:
    return LookedButtonData(*raw_data.replace('looked ', '').split(','))
