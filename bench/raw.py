import json
from functools import partial
from typing import Any

import data
from dataclasses_class import LARGE, MEDIUM, SMALL, Large, Medium, Small
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
        se = se_medium  # type: ignore[assignment]
        de = de_medium
        astuple = astuple_medium  # type: ignore[assignment]
        asdict = asdict_medium  # type: ignore[assignment]
    elif size == Size.Large:
        unp = LARGE
        pac = data.LARGE
        se = se_large  # type: ignore[assignment]
        de = de_large
        astuple = astuple_large  # type: ignore[assignment]
        asdict = asdict_large  # type: ignore[assignment]
    return Runner(
        name, unp, partial(se, unp), partial(de, pac), partial(astuple, unp), partial(asdict, unp)
    )


def se_small(s: Small) -> str:
    return json.dumps(asdict_small(s))


def se_medium(m: Medium) -> str:
    return json.dumps({"inner": [{"i": s.i, "s": s.s, "f": s.f, "b": s.b} for s in m.inner]})


def de_small(data: str) -> Small:
    return _de_small(json.loads(data))


def _de_small(dct: dict[str, Any]) -> Small:
    return Small(dct["i"], dct["s"], dct["f"], dct["b"])


def de_medium(data: str) -> Medium:
    lst = json.loads(data)
    return Medium([_de_small(v) for v in lst["inner"]])


def astuple_small(sm: Small) -> tuple[int, str, float, bool]:
    return (sm.i, sm.s, sm.f, sm.b)


def astuple_medium(md: Medium) -> tuple[list[tuple[int, str, float, bool]]]:
    return ([astuple_small(sm) for sm in md.inner],)


def asdict_small(s: Small) -> dict[str, Any]:
    return {"i": s.i, "s": s.s, "f": s.f, "b": s.b}


def asdict_medium(m: Medium) -> dict[str, Any]:
    return {"inner": [asdict_small(s) for s in m.inner]}


def se_large(large: Large) -> str:
    return json.dumps(asdict_large(large))


def de_large(data: str) -> Large:
    return _de_large(json.loads(data))


def _de_large(dct: dict[str, Any]) -> Large:
    return Large(
        customer_id=dct["customer_id"],
        name=dct["name"],
        email=dct["email"],
        preferences=dct["preferences"],
        items_list=dct["items_list"],
        nested_data=dct["nested_data"],
        loyalty_points=dct["loyalty_points"],
        created_at=dct["created_at"],
    )


def astuple_large(large: Large) -> tuple[Any, ...]:
    # Complex tuple conversion for large nested structure
    from dataclasses import astuple

    return astuple(large)


def asdict_large(large: Large) -> dict[str, Any]:
    # Complex dict conversion for large nested structure
    from dataclasses import asdict

    return asdict(large)
