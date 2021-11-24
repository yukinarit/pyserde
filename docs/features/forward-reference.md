# Forward reference

You can use a forward reference in annotations.

```python
class Foo:
    i: int
    s: str
    bar: 'Bar'  # Specify type annotation in string.

@serde
class Bar:
    f: float
    b: bool

# Evaluate pyserde decorators after `Bar` is defined.
serde(Foo)
```

For complete example, please see [examples/forward_reference.py](https://github.com/yukinarit/pyserde/blob/master/examples/forward_reference.py)
