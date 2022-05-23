# Python 3.9 type hinting

For python >= 3.9, you can use [PEP585](https://www.python.org/dev/peps/pep-0585/) style type annotations for standard collections.

```python
@serde
@dataclass
class Foo:
    i: int
    l: list[str]
    t: tuple[int, float, str, bool]
    d: dict[str, list[tuple[str, int]]]
    o: Optional[str]
    nested: Bar
```

For complete example, please see [examples/collection.py](https://github.com/yukinarit/pyserde/blob/master/examples/collection.py)
