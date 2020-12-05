from pydantic import BaseModel

import data
import json
from typing import List, Type, Union
from functools import partial
from runner import Size, Runner


class Small(BaseModel):
    i: int
    s: str
    f: float
    b: bool


class Medium(BaseModel):
    inner: List[Small]


SMALL = Small(**data.args_sm)

MEDIUM = Medium(inner=[Small(**d) for d in data.args_md])


def new(size: Size) -> Runner:
    name = 'pydantic'
    if size == Size.Small:
        unp = SMALL
        pac = data.SMALL
        cls = Small
    elif size == Size.Medium:
        unp = MEDIUM
        pac = data.MEDIUM
        cls = Medium
    return Runner(name, unp, partial(se, unp), partial(de, cls, pac), None, partial(asdict, unp))


def se(obj: Union[Small, Medium]):
    return obj.json()


def de(cls: Type, data: str):
    return cls.parse_obj(json.loads(data))


def asdict(obj: Union[Small, Medium]):
    return obj.dict()
