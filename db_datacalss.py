from dataclasses import dataclass

import typing


@dataclass
class SourceData:
    id: int
    id_tv_show: int
    site_name: str
    url: str
    encoding: typing.Optional[str] = None
