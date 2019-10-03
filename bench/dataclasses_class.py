import json
import dataclasses
from dataclasses import dataclass, field
from typing import List, Type


@dataclass
class Small:
    i: int
    s: str
    f: float
    b: bool


@dataclass
class Medium:
    inner: List[Small] = field(default_factory=list)


def se(cls: Type, **kwargs):
    c = cls(**kwargs)
    return json.dumps(asdict(c))


def astuple(d):
    return dataclasses.astuple(d)


def asdict(d):
    return dataclasses.asdict(d)
