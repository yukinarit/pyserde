from dataclasses import dataclass
from dataclasses_json import dataclass_json

import data
from dataclasses import dataclass, field
from typing import List, Type, Union
from functools import partial
from runner import Size, Runner


@dataclass_json
@dataclass
class Small:
    i: int
    s: str
    f: float
    b: bool


@dataclass_json
@dataclass
class Medium:
    inner: List[Small] = field(default_factory=list)


SMALL = Small(**data.args_sm)

MEDIUM = Medium([Small(**d) for d in data.args_md])


def new(size: Size) -> Runner:
    name = 'dataclasses_json'
    if size == Size.Small:
        unp = SMALL
        pac = data.SMALL
        cls = Small
    elif size == Size.Medium:
        unp = MEDIUM
        pac = data.MEDIUM
        cls = Medium
    return Runner(name, unp, partial(se, unp), partial(de, cls, pac), None, None)


def se(obj: Union[Small, Medium]):
    return obj.to_json()


def de(cls: Type, data: str):
    return cls.from_json(data)
