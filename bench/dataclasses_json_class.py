import dataclasses_json
from dataclasses import dataclass, field
from typing import List, Type
from data import args_sm


@dataclasses_json.dataclass_json
@dataclass
class Small:
    i: int
    s: str
    f: float
    b: bool


@dataclasses_json.dataclass_json
@dataclass
class Medium:
    inner: List[Small] = field(default_factory=list)


def de(cls: Type, data: str):
    return cls.from_json(data)


def se(cls: Type, **kwargs):
    c = cls(**args_sm)
    return c.to_json()
