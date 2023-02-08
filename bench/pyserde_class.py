from dataclasses import dataclass, field
from functools import partial
from typing import List, Type, Union

import data
from runner import Runner, Size

import serde
import serde.json


@serde.serde
@dataclass(unsafe_hash=True)
class Small:
    i: int
    s: str
    f: float
    b: bool


@serde.serde
@dataclass
class Medium:
    inner: List[Small] = field(default_factory=list)


SMALL = Small(**data.args_sm)

MEDIUM = Medium([Small(**d) for d in data.args_md])


def new(size: Size) -> Runner:
    name = 'pyserde'
    if size == Size.Small:
        unp = SMALL
        pac = data.SMALL
        cls = Small
    elif size == Size.Medium:
        unp = MEDIUM
        pac = data.MEDIUM
        cls = Medium
    return Runner(name, unp, partial(se, unp), partial(de, cls, pac), partial(astuple, unp), partial(asdict, unp))


def se(obj: Union[Small, Medium]):
    return serde.json.to_json(obj)


def de(cls: Type, data: str):
    return serde.json.from_json(cls, data)


def astuple(data):
    return serde.to_tuple(data)


def asdict(data):
    return serde.to_dict(data)
