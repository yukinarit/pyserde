# Alias

You can set aliases for field names. Alias only works for deserialization.

```python
@serde
@dataclass
class Foo:
    a: str = field(alias=["b", "c"])
```

`Foo` can be deserialized from either `{"a": "..."}`, `{"b": "..."}` or `{"c": "..."}`.

For complete example, please see [examples/alias.py](https://github.com/yukinarit/pyserde/blob/main/examples/alias.py)
