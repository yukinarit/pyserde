import json
import dacite
import data
from typing import Type
from dataclasses_class import SMALL, MEDIUM, Small, Medium
from functools import partial
from runner import Size, Runner


def de(cls: Type, data: str):
    return dacite.from_dict(data_class=cls, data=json.loads(data))


def new(size: Size) -> Runner:
    name = 'attrs'
    if size == Size.Small:
        unp = SMALL
        pac = data.SMALL
        cls = Small
    elif size == Size.Medium:
        unp = MEDIUM
        pac = data.MEDIUM
        cls = Medium
    return Runner(name, unp, None, partial(de, cls, pac), None, None)
