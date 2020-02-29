import cattr
import json
import data
from attrs_class import Small, Medium, SMALL, MEDIUM
from typing import Union, Type
from functools import partial
from runner import Size, Runner


def new(size: Size) -> Runner:
    name = 'cattrs'
    if size == Size.Small:
        unp = SMALL
        pac = data.SMALL
        cls = Small
    elif size == Size.Medium:
        unp = MEDIUM
        pac = data.MEDIUM
        cls = Medium
    return Runner(name, unp, partial(se, unp), partial(de, cls, pac), None, partial(asdict, unp))


def se(obj: Union[Small, Medium]):
    return json.dumps(cattr.unstructure(obj))


def de(cls: Type, data: str):
    return cattr.structure(json.loads(data), cls)


def asdict(obj: Union[Small, Medium]):
    return cattr.unstructure(obj)
