import json
from functools import partial
from typing import Any, Union

import cattrs
import data
from attrs_class import LARGE, MEDIUM, SMALL, Large, Medium, Small
from runner import Runner, Size


def new(size: Size) -> Runner:
    name = "cattrs"
    if size == Size.Small:
        unp = SMALL
        pac = data.SMALL
        cls = Small
    elif size == Size.Medium:
        unp = MEDIUM
        pac = data.MEDIUM
        cls = Medium
    elif size == Size.Large:
        unp = LARGE
        pac = data.LARGE
        cls = Large
        # Skip deserialization for Large due to Union type issues
        return Runner(name, unp, partial(se, unp), None, None, partial(asdict, unp))
    return Runner(name, unp, partial(se, unp), partial(de, cls, pac), None, partial(asdict, unp))


def se(obj: Union[Small, Medium, Large]) -> str:
    return json.dumps(cattrs.unstructure(obj))


def de(cls: type, data: str) -> Union[Small, Medium, Large]:
    return cattrs.structure(json.loads(data), cls)


def asdict(obj: Union[Small, Medium, Large]) -> dict[str, Any]:
    return cattrs.unstructure(obj)  # type: ignore[no-any-return]
