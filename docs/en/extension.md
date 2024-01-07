# Extending pyserde

pyserde offers three ways to extend pyserde to support non builtin types.

## Custom field (de)serializer

See [custom field serializer](./field-attributes.md#serializerdeserializer).

> 💡 Tip: wrapping `serde.field` with your own field function makes 
>
> ```python
> import serde
>
> def field(*args, **kwargs):
>     serde.field(*args, **kwargs, serializer=str)
>
> @serde
> class Foo:
>     a: int = field(default=0)  # Configuring field serializer
> ```

## Custom class (de)serializer

See [custom class serializer](./class-attributes.md#class_serializer--class_deserializer).

## Custom global (de)serializer

You apply the custom (de)serialization for entire codebase by registering class (de)serializer by `add_serializer` and `add_deserializer`. Registered class (de)serializers are stacked in pyserde's global space and automatically used for all the pyserde classes.

e.g. Implementing custom (de)serialization for `datetime.timedelta` using [isodate](https://pypi.org/project/isodate/) package.

Here is the code of registering class (de)serializer for `datetime.timedelta`. This package is actually published in PyPI as [pyserde-timedelta](https://pypi.org/project/pyserde-timedelta/).

```python
from datetime import timedelta
from plum import dispatch
from typing import Type, Any
import isodate
import serde

class Serializer:
    @dispatch
    def serialize(self, value: timedelta) -> Any:
        return isodate.duration_isoformat(value)

class Deserializer:
    @dispatch
    def deserialize(self, cls: Type[timedelta], value: Any) -> timedelta:
        return isodate.parse_duration(value)

def init() -> None:
    serde.add_serializer(Serializer())
    serde.add_deserializer(Deserializer())
```

Users of this package can reuse custom (de)serialization functionality for `datetime.timedelta` just by calling `serde_timedelta.init()`.

```python
import serde_timedelta
from serde import serde
from serde.json import to_json, from_json
from datetime import timedelta

serde_timedelta.init()

@serde
class Foo:
    a: timedelta

f = Foo(timedelta(hours=10))
json = to_json(f)
print(json)
print(from_json(Foo, json))
```
and you get `datetime.timedelta` to be serialized in ISO 8601 duration format!
```bash
{"a":"PT10H"}
Foo(a=datetime.timedelta(seconds=36000))
```

> 💡 Tip: You can register as many class (de)serializer as you want. This means you can use as many pyserde extensions as you want.
>  Registered (de)serializers are stacked in the memory. A (de)serializer can be overridden by another (de)serializer.
>
> e.g. If you register 3 custom serializers in this order, the first serializer will completely overridden by the 3rd one. 2nd one works because it is implemented for a different type.
> 1. Register Serializer for `int`
> 2. Register Serializer for `float`
> 3. Register Serializer for `int`

New in v0.13.0.
