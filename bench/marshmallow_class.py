import json
from functools import partial
from typing import Union

import data
import marshmallow as ms
from dataclasses_class import MEDIUM, SMALL, Medium, Small
from runner import Runner, Size


class SmallSchema(ms.Schema):
    class Meta:
        render_module = json

    i = ms.fields.Int()
    s = ms.fields.Str()
    f = ms.fields.Float()
    b = ms.fields.Boolean()

    @ms.post_load
    def make_small(self, data, **kwargs):
        return Small(**data)


class MediumSchema(ms.Schema):
    class Meta:
        render_module = json

    inner = ms.fields.List(ms.fields.Nested(SmallSchema))

    @ms.post_load
    def make_medium(self, data, **kwargs):
        return Medium([s for s in data["inner"]])


def new(size: Size) -> Runner:
    name = "marshmallow"
    if size == Size.Small:
        unp = SMALL
        pac = data.SMALL
        schema = SmallSchema()
    elif size == Size.Medium:
        unp = MEDIUM
        pac = data.MEDIUM
        schema = MediumSchema()
    return Runner(
        name,
        unp,
        partial(se, schema, unp),
        partial(de, schema, pac),
        None,
        partial(asdict, schema, unp),
    )


def se(schema: ms.Schema, obj: Union[Small, Medium]):
    return schema.dumps(obj)


def de(schema: ms.Schema, data: str):
    return schema.loads(data)


def asdict(schema: ms.Schema, data: str):
    return schema.dump(data)
