import serde
import serde.json
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Type


@serde.serialize
@serde.deserialize
@dataclass
class SerdeSmall:
    i: int
    s: str
    f: float
    b: bool


@serde.serialize
@serde.deserialize
@dataclass
class SerdeMedium:
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


@serde.serialize
@serde.deserialize
@dataclass
class SerdePriContainer:
    v: List[int] = field(default_factory=list)
    d: Dict[str, int] = field(default_factory=dict)
    t: Tuple[bool] = field(default_factory=tuple)


def de_pyserde(cls: Type, data: str):
    return serde.json.from_json(cls, data)


def se_pyserde(cls: Type, **kwargs):
    return serde.json.to_json(cls(**kwargs))


def astuple_pyserde(data):
    return serde.astuple(data)


def asdict_pyserde(data):
    return serde.asdict(data)
