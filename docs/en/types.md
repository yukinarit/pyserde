# Types

Here is the list of the supported types. See the simple example for each type in the footnotes

* Primitives (int, float, str, bool) [^1]
* Containers
    * `List`, `Set`, `Tuple`, `Dict` [^2]
    * [`FrozenSet`](https://docs.python.org/3/library/stdtypes.html#frozenset), [^3] [`DefaultDict`](https://docs.python.org/3/library/collections.html#collections.defaultdict) [^4]
* [`typing.Optional`](https://docs.python.org/3/library/typing.html#typing.Optional) [^5]
* [`typing.Union`](https://docs.python.org/3/library/typing.html#typing.Union) [^6] [^7] [^8]
* User defined class with [`@dataclass`](https://docs.python.org/3/library/dataclasses.html) [^9] [^10]
* [`typing.NewType`](https://docs.python.org/3/library/typing.html#newtype) for primitive types [^11]
* [`typing.Any`](https://docs.python.org/3/library/typing.html#the-any-type) [^12]
* [`typing.Literal`](https://docs.python.org/3/library/typing.html#typing.Literal) [^13]
* [`typing.Generic`](https://docs.python.org/3/library/typing.html#user-defined-generic-types) [^14]
* [`typing.ClassVar`](https://docs.python.org/3/library/typing.html#typing.ClassVar) [^15]
* [`typing.InitVar`](https://docs.python.org/3/library/dataclasses.html#init-only-variables) [^16]
* [`Enum`](https://docs.python.org/3/library/enum.html#enum.Enum) and [`IntEnum`](https://docs.python.org/3/library/enum.html#enum.IntEnum) [^17]
* Standard library
    * [`pathlib.Path`](https://docs.python.org/3/library/pathlib.html)
    * [`decimal.Decimal`](https://docs.python.org/3/library/decimal.html) [^18]
    * [`uuid.UUID`](https://docs.python.org/3/library/uuid.html)
    * [`datetime.date`](https://docs.python.org/3/library/datetime.html#date-objects), [`datetime.time`](https://docs.python.org/3/library/datetime.html#time-objects), [`datetime.datetime`](https://docs.python.org/3/library/datetime.html#datetime-objects) [^19]
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
    a: int
    b: list[str]
    c: tuple[int, float, str, bool]
    d: dict[str, list[tuple[str, int]]]
    e: str | None
    f: Bar
```

## Numpy

All of the above (de)serialization methods can transparently handle most numpy types with the "numpy" extras package.

```python
import numpy as np
import numpy.typing as npt

@serde
class NPFoo:
    i: np.int32
    j: np.int64
    f: np.float32
    g: np.float64
    h: np.bool_
    u: np.ndarray
    v: npt.NDArray
    w: npt.NDArray[np.int32]
    x: npt.NDArray[np.int64]
    y: npt.NDArray[np.float32]
    z: npt.NDArray[np.float64]

npfoo = NPFoo(
    np.int32(1),
    np.int64(2),
    np.float32(3.0),
    np.float64(4.0),
    np.bool_(False),
    np.array([1, 2]),
    np.array([3, 4]),
    np.array([np.int32(i) for i in [1, 2]]),
    np.array([np.int64(i) for i in [3, 4]]),
    np.array([np.float32(i) for i in [5.0, 6.0]]),
    np.array([np.float64(i) for i in [7.0, 8.0]]),
)
```

```python
>>> from serde.json import to_json, from_json

>>> to_json(npfoo)
'{"i": 1, "j": 2, "f": 3.0, "g": 4.0, "h": false, "u": [1, 2], "v": [3, 4], "w": [1, 2], "x": [3, 4], "y": [5.0, 6.0], "z": [7.0, 8.0]}'

>>> from_json(NPFoo, to_json(npfoo))
NPFoo(i=1, j=2, f=3.0, g=4.0, h=False, u=array([1, 2]), v=array([3, 4]), w=array([1, 2], dtype=int32), x=array([3, 4]), y=array([5., 6.], dtype=float32), z=array([7., 8.]))
```

## Needs a new type support?

If you need to use a type which is currently not supported in the standard library, please creat a Github issue to request. For types in third party python packages, unless it's polular like numpy, we don't plan to support it to keep pyserde as simple as possible. We recommend to use custom class or field serializer.

[^1]: See [examples/simple.py](https://github.com/yukinarit/pyserde/blob/main/examples/simple.py)

[^2]: See [examples/collection.py](https://github.com/yukinarit/pyserde/blob/main/examples/collection.py)

[^3]: See [examples/frozen_set.py](https://github.com/yukinarit/pyserde/blob/main/examples/frozen_set.py)

[^4]: See [examples/default_dict.py](https://github.com/yukinarit/pyserde/blob/main/examples/default_dict.py)

[^6]: See [examples/union.py](https://github.com/yukinarit/pyserde/blob/main/examples/union.py)

[^7]: See [examples/union_operator.py](https://github.com/yukinarit/pyserde/blob/main/examples/union_operator.py)

[^8]: See [examples/union_tagging.py](https://github.com/yukinarit/pyserde/blob/main/examples/union_tagging.py)

[^9]: See [examples/simple.py](https://github.com/yukinarit/pyserde/blob/main/examples/simple.py)

[^10]: See [examples/nested.py](https://github.com/yukinarit/pyserde/blob/main/examples/nested.py)

[^11]: See [examples/newtype.py](https://github.com/yukinarit/pyserde/blob/main/examples/newtype.py)

[^12]: See [examples/any.py](https://github.com/yukinarit/pyserde/blob/main/examples/any.py)

[^13]: See [examples/literal.py](https://github.com/yukinarit/pyserde/blob/main/examples/literal.py)

[^14]: See [examples/generics.py](https://github.com/yukinarit/pyserde/blob/main/examples/generics.py)

[^15]: See [examples/class_var.py](https://github.com/yukinarit/pyserde/blob/main/examples/class_var.py)

[^16]: See [examples/init_var.py](https://github.com/yukinarit/pyserde/blob/main/examples/init_var.py)

[^17]: See [examples/enum34.py](https://github.com/yukinarit/pyserde/blob/main/examples/enum34.py)

[^18]: See [examples/type_decimal.py](https://github.com/yukinarit/pyserde/blob/main/examples/type_decimal.py)

[^19]: See [examples/type_datetime.py](https://github.com/yukinarit/pyserde/blob/main/examples/type_datetime.py)
