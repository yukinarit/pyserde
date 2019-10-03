import json
import dacite
from dataclasses import asdict
from typing import Type
from data import args_sm


def de(cls: Type, data: str):
    return dacite.from_dict(data_class=cls, data=json.loads(data))


def se(cls: Type, **kwargs):
    c = cls(**args_sm)
    return json.dumps(asdict(c))
