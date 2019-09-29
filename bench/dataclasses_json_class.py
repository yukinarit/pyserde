import json
import dataclasses_json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Tuple, Type
from data import args_sm


@dataclasses_json.dataclass_json
@dataclass
class DJsonSmall:
    i: int
    s: str
    f: float
    b: bool


@dataclasses_json.dataclass_json
@dataclass
class DJsonMedium:
    i: int
    s: str
    f: float
    b: bool
    i2: int
    s2: str
    f2: float
    b2: bool
    i3: int
    s3: str
    f3: float
    b3: bool
    i4: int
    s4: str
    f4: float
    b4: bool
    i5: int
    s5: str
    f5: float
    b5: bool


@dataclasses_json.dataclass_json
@dataclass
class DJsonPriContainer:
    v: List[int] = field(default_factory=list)
    d: Dict[str, int] = field(default_factory=dict)
    t: Tuple = field(default_factory=tuple)


def de_dataclasses_json(cls: Type, data: str):
    return cls.from_json(data)


def se_dataclasses_json(cls: Type, **kwargs):
    c = cls(**args_sm)
    return c.to_json()
