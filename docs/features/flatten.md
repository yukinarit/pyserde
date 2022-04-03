# Flatten

You can flatten the fields of the nested structure.

```python
@serde
@dataclass
class Bar:
    c: float
    d: bool

@serde
@dataclass
class Foo:
    a: int
    b: str
    bar: Bar = field(metadata={'serde_flatten': True})
```

Bar's c, d fields will be deserialized as if they are defined in Foo.

For complete example, please see [examples/flatten.py](https://github.com/yukinarit/pyserde/blob/master/examples/flatten.py)
