from typing import List, Callable

from middleware import db_session_middleware
from tests.mock.middleware import db_session_middleware_mock


def modify_middleware(middlewares: List[Callable]):
    index_db_session_middleware = middlewares.index(db_session_middleware)
    middlewares[index_db_session_middleware] = db_session_middleware_mock
    return middlewares
