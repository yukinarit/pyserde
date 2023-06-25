import json
from functools import partial
from typing import List, Tuple

import data
from dataclasses_class import MEDIUM, SMALL, Medium, Small
from runner import Runner, Size


def new(size: Size) -> Runner:
    name = "raw"
    if size == Size.Small:
        unp = SMALL
        pac = data.SMALL
        se = se_small
        de = de_small
        astuple = astuple_small
        asdict = asdict_small
    elif size == Size.Medium:
        unp = MEDIUM
        pac = data.MEDIUM
        se = se_medium
        de = de_medium
        astuple = astuple_medium
        asdict = asdict_medium
    return Runner(
        name, unp, partial(se, unp), partial(de, pac), partial(astuple, unp), partial(asdict, unp)
    )


def se_small(s: Small):
    return json.dumps(asdict_small(s))


def se_medium(m: Medium):
    return json.dumps({"inner": [{"i": s.i, "s": s.s, "f": s.f, "b": s.b} for s in m.inner]})


def de_small(data: str) -> Small:
    return _de_small(json.loads(data))


def _de_small(dct) -> Small:
    return Small(dct["i"], dct["s"], dct["f"], dct["b"])


def de_medium(data: str) -> Medium:
    lst = json.loads(data)
    return Medium([_de_small(v) for v in lst["inner"]])


def astuple_small(sm: Small) -> Tuple[int, str, float, bool]:
    return (sm.i, sm.s, sm.f, sm.b)


def astuple_medium(md: Medium) -> Tuple[List[Tuple[int, str, float, bool]]]:
    return ([astuple_small(sm) for sm in md.inner],)


def asdict_small(s: Small):
    return {"i": s.i, "s": s.s, "f": s.f, "b": s.b}


def asdict_medium(m: Medium):
    return {"inner": [asdict_small(s) for s in m.inner]}
