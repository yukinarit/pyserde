import json
from functools import partial
from typing import Any, Union

import data
import marshmallow as ms
from dataclasses_class import LARGE, MEDIUM, SMALL, Large, Medium, Small
from runner import Runner, Size


class SmallSchema(ms.Schema):
    class Meta:
        render_module = json

    i = ms.fields.Int()
    s = ms.fields.Str()
    f = ms.fields.Float()
    b = ms.fields.Boolean()

    @ms.post_load
    def make_small(self, data: dict[str, Any], **kwargs: Any) -> Small:
        return Small(**data)


class MediumSchema(ms.Schema):
    class Meta:
        render_module = json

    inner = ms.fields.List(ms.fields.Nested(SmallSchema))

    @ms.post_load
    def make_medium(self, data: dict[str, Any], **kwargs: Any) -> Medium:
        return Medium(list(data["inner"]))


class LargeSchema(ms.Schema):
    class Meta:
        render_module = json

    customer_id = ms.fields.Int()
    name = ms.fields.Str()
    email = ms.fields.Str()
    preferences = ms.fields.Dict()
    items_list = ms.fields.List(ms.fields.Str())
    nested_data = ms.fields.Dict()
    loyalty_points = ms.fields.Int()
    created_at = ms.fields.Str()

    @ms.post_load
    def make_large(self, data: dict[str, Any], **kwargs: Any) -> Large:
        return Large(**data)


def new(size: Size) -> Runner:
    name = "marshmallow"
    if size == Size.Small:
        unp = SMALL
        pac = data.SMALL
        schema = SmallSchema()
    elif size == Size.Medium:
        unp = MEDIUM
        pac = data.MEDIUM
        schema = MediumSchema()  # type: ignore[assignment]
    elif size == Size.Large:
        unp = LARGE
        pac = data.LARGE
        schema = LargeSchema()  # type: ignore[assignment]
    return Runner(
        name,
        unp,
        partial(se, schema, unp),
        partial(de, schema, pac),
        None,
        partial(asdict, schema, unp),
    )


def se(schema: ms.Schema, obj: Union[Small, Medium, Large]) -> str:
    return schema.dumps(obj)  # type: ignore[no-any-return]


def de(schema: ms.Schema, data: str) -> Union[Small, Medium, Large]:
    return schema.loads(data)


def asdict(schema: ms.Schema, obj: Union[Small, Medium, Large]) -> dict[str, Any]:
    return schema.dump(obj)  # type: ignore[no-any-return]
