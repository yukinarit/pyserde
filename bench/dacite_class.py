import json
from functools import partial
from typing import Union

import dacite
import data
from dataclasses_class import LARGE, MEDIUM, SMALL, Large, Medium, Small
from runner import Runner, Size


def de(cls: type, data: str) -> Union[Small, Medium, Large]:
    return dacite.from_dict(data_class=cls, data=json.loads(data))


def new(size: Size) -> Runner:
    name = "dacite"
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
    return Runner(name, unp, None, partial(de, cls, pac), None, None)
