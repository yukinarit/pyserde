# 使用可能な型

* プリミティブ (int, float, str, bool)
* コンテナ
    * `List`, `Set`, `Tuple`, `Dict`
    * [`FrozenSet`](https://docs.python.org/3/library/stdtypes.html#frozenset), [`DefaultDict`](https://docs.python.org/3/library/collections.html#collections.defaultdict)
* [`typing.Optional`](https://docs.python.org/3/library/typing.html#typing.Optional)
* [`typing.Union`](https://docs.python.org/3/library/typing.html#typing.Union)
* ユーザーが定義した[`@dataclass`](https://docs.python.org/3/library/dataclasses.html)
* [`typing.NewType`](https://docs.python.org/3/library/typing.html#newtype) (プリミティブのみ)
* [`typing.Any`](https://docs.python.org/3/library/typing.html#the-any-type)
* [`typing.Literal`](https://docs.python.org/3/library/typing.html#typing.Literal)
* [`typing.Generic`](https://docs.python.org/3/library/typing.html#user-defined-generic-types)
* [`typing.ClassVar`](https://docs.python.org/3/library/typing.html#user-defined-generic-type://docs.python.org/3/library/typing.html#typing.ClassVar)
* [`Enum`](https://docs.python.org/3/library/enum.html#enum.Enum)と[`IntEnum`](https://docs.python.org/3/library/enum.html#enum.IntEnum)
* 標準ライブラリ
    * [`pathlib.Path`](https://docs.python.org/3/library/pathlib.html)
    * [`decimal.Decimal`](https://docs.python.org/3/library/decimal.html)
    * [`uuid.UUID`](https://docs.python.org/3/library/uuid.html)
    * [`datetime.date`](https://docs.python.org/3/library/datetime.html#date-objects), [`datetime.time`](https://docs.python.org/3/library/datetime.html#time-objects), [`datetime.datetime`](https://docs.python.org/3/library/datetime.html#datetime-objects)
    * [`ipaddress`](https://docs.python.org/3/library/ipaddress.html)
* PyPIライブラリ
    * [`numpy`](https://github.com/numpy/numpy) types

このような様々な型を使った複雑なクラスも表現可能です。
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

## Numpy

`numpy`のほとんどの型もpyserdeの機能が使えるようになっています。

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
