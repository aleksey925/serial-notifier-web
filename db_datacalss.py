from dataclasses import dataclass

import typing


@dataclass
class SourceData:
    id: int
    site_name: str
    tv_show_name: str
    url: str
    encoding: typing.Optional[str] = None
