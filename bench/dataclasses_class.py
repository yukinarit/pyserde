import dataclasses
import json
from dataclasses import dataclass, field
from functools import partial
from typing import List, Union

import data
from runner import Runner, Size


@dataclass
class Small:
    i: int
    s: str
    f: float
    b: bool


@dataclass
class Medium:
    inner: List[Small] = field(default_factory=list)


SMALL = Small(**data.args_sm)

MEDIUM = Medium([Small(**d) for d in data.args_md])


def new(size: Size) -> Runner:
    name = 'dataclass'
    if size == Size.Small:
        unp = SMALL
    elif size == Size.Medium:
        unp = MEDIUM
    return Runner(name, unp, partial(se, unp), None, partial(astuple, unp), partial(asdict, unp))


def se(obj: Union[Small, Medium]):
    return json.dumps(asdict(obj))


def astuple(d):
    return dataclasses.astuple(d)


def asdict(d):
    return dataclasses.asdict(d)
