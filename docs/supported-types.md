# Supported types

* Primitives (int, float, str, bool)
* Containers (List, Set, Tuple, Dict)
* [`typing.Optional`](https://docs.python.org/3/library/typing.html#typing.Optional)
* [`typing.Union`](https://docs.python.org/3/library/typing.html#typing.Union)
* User defined class with [`@dataclass`](https://docs.python.org/3/library/dataclasses.html)
* [`typing.NewType`](https://docs.python.org/3/library/typing.html#newtype) for primitive types
* [`typing.Any`](https://docs.python.org/3/library/typing.html#the-any-type)
* [`Enum`](https://docs.python.org/3/library/enum.html#enum.Enum) and [`IntEnum`](https://docs.python.org/3/library/enum.html#enum.IntEnum)
* More types
    * [`pathlib.Path`](https://docs.python.org/3/library/pathlib.html)
    * [`decimal.Decimal`](https://docs.python.org/3/library/decimal.html)
    * [`uuid.UUID`](https://docs.python.org/3/library/uuid.html)
    * [`datetime.date`](https://docs.python.org/3/library/datetime.html#date-objects) & [`datetime.datetime`](https://docs.python.org/3/library/datetime.html#datetime-objects)
    * [`ipaddress`](https://docs.python.org/3/library/ipaddress.html)

You can write pretty complex class like this:
```python
@deserialize
@serialize
@dataclass
class bar:
    i: int

@deserialize
@serialize
class Foo:
    i: int
    l: List[str]
    t: Tuple[int, float, str, bool]
    d: Dict[str, List[Tuple[str, int]]]
    o: Optional[str]
    nested: Bar
```
