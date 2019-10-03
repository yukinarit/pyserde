import json
from typing import Type, Tuple, List

import data
from dataclasses_class import Small, Medium


def se_small(cls: Type, **kwargs):
    c = Small(**kwargs)
    return json.dumps({'i': c.i, 's': c.s, 'f': c.f, 'b': c.b})


def de_small() -> Small:
    dct = json.loads(data.SMALL)
    return _de_small(dct)


def _de_small(dct) -> Small:
    return Small(dct['i'], dct['s'], dct['f'], dct['b'])


def de_medium() -> Medium:
    lst = json.loads(data.MEDIUM)
    return Medium([_de_small(v) for v in lst['inner']])


def astuple_small(sm: Small) -> Tuple[int, str, float, bool]:
    return (sm.i, sm.s, sm.f, sm.b)


def astuple_medium(md: Medium) -> Tuple[List[Tuple[int, str, float, bool]]]:
    return ([astuple_small(sm) for sm in md.inner],)
