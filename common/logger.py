import logging


def root_logger_cleaner():
    """
    Сбрасывает root логгер к настройкам, которые были у root логгера при
    инициализации коррутины
    """
    root = logging.getLogger()
    default_settings = {
        'level': root.level,
        'disabled': root.disabled,
        'propagate': root.propagate,
        'filters': root.filters[:],
        'handlers': root.handlers[:],
    }
    yield

    while True:
        for attr, attr_value in default_settings.items():
            setattr(root, attr, attr_value)
        yield
