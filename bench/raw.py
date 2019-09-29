import json
from dataclasses import dataclass, field, astuple, asdict
from typing import List, Dict, Tuple, Type
from tests.data import Pri
from data import json_sm, json_md, json_pri_container


@dataclass
class RawMedium:
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


@dataclass
class RawPriContainer:
    v: List[int] = field(default_factory=list)
    d: Dict[str, int] = field(default_factory=dict)
    t: Tuple = field(default_factory=tuple)


def de_raw_small():
    dct = json.loads(json_sm)
    return Pri(dct['i'], dct['s'], dct['f'], dct['b'])


def de_raw_medium():
    dct = json.loads(json_md)
    return RawMedium(
        dct['i'],
        dct['s'],
        dct['f'],
        dct['b'],
        dct['i2'],
        dct['s2'],
        dct['f2'],
        dct['b2'],
        dct['i3'],
        dct['s3'],
        dct['f3'],
        dct['b3'],
        dct['i4'],
        dct['s4'],
        dct['f4'],
        dct['b4'],
        dct['i5'],
        dct['s5'],
        dct['f5'],
        dct['b5'],
    )


def de_raw_pri_container():
    dct = json.loads(json_pri_container)
    return RawPriContainer(dct['v'], dct['d'], dct['t'])


def se_raw_small(cls: Type, **kwargs):
    c = Pri(**kwargs)
    return json.dumps({'i': c.i, 's': c.s, 'f': c.f, 'b': c.b})


def astuple_raw(data):
    return astuple(data)


def asdict_raw(data):
    return asdict(data)


def astuple_dataclass(data):
    return astuple(data)


def se_dataclass(cls: Type, **kwargs):
    c = cls(**kwargs)
    return json.dumps(asdict(c))
