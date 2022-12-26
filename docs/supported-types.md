# Supported types

* Primitives (int, float, str, bool)
* Containers
    * List, Set, Tuple, Dict
    * FrozenSet
* [`typing.Optional`](https://docs.python.org/3/library/typing.html#typing.Optional)
* [`typing.Union`](https://docs.python.org/3/library/typing.html#typing.Union)
* User defined class with [`@dataclass`](https://docs.python.org/3/library/dataclasses.html)
* [`typing.NewType`](https://docs.python.org/3/library/typing.html#newtype) for primitive types
* [`typing.Any`](https://docs.python.org/3/library/typing.html#the-any-type)
* [`typing.Literal`](https://docs.python.org/3/library/typing.html#typing.Literal)
* [`typing.Generic`](https://docs.python.org/3/library/typing.html#user-defined-generic-types)
* [`Enum`](https://docs.python.org/3/library/enum.html#enum.Enum) and [`IntEnum`](https://docs.python.org/3/library/enum.html#enum.IntEnum)
* Standard library
    * [`pathlib.Path`](https://docs.python.org/3/library/pathlib.html)
    * [`decimal.Decimal`](https://docs.python.org/3/library/decimal.html)
    * [`uuid.UUID`](https://docs.python.org/3/library/uuid.html)
    * [`datetime.date`](https://docs.python.org/3/library/datetime.html#date-objects), [`datetime.time`](https://docs.python.org/3/library/datetime.html#time-objects), [`datetime.datetime`](https://docs.python.org/3/library/datetime.html#datetime-objects)
    * [`ipaddress`](https://docs.python.org/3/library/ipaddress.html)
* PyPI library
    * [`numpy`](https://github.com/numpy/numpy) types

You can write pretty complex class like this:
```python
@serde
@dataclass
class bar:
    i: int

@serde
@dataclass
class Foo:
    i: int
    l: List[str]
    t: Tuple[int, float, str, bool]
    d: Dict[str, List[Tuple[str, int]]]
    o: Optional[str]
    nested: Bar
```
