import logging
import logging.handlers

import structlog

# Порядок процессоров не менять без явной необходимости
simple_processors = [
    structlog.stdlib.filter_by_level,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.UnicodeDecoder(),
    structlog.processors.format_exc_info,
    structlog.dev.ConsoleRenderer(),
]

simple_formatter = logging.Formatter('%(levelname)s %(asctime)s - %(module)s:%(lineno)d - %(message)s')


def _init_structlog(processors):
    structlog.configure(
        processors=processors,
        context_class=structlog.threadlocal.wrap_dict(dict),
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def _init_logging(default_formatter):
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(default_formatter)

    root_logger.addHandler(console_handler)


def init_logger():
    processors = simple_processors
    formatter = simple_formatter

    _init_logging(formatter)
    _init_structlog(processors)
