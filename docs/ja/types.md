# Types

以下はサポートされている型のリストです。各型の簡単な例は脚注にあります。

* プリミティブ（`int`, `float`, `str`, `bool`）[^1]
* コンテナ
    * `list`, `collections.abc.Sequence`, `collections.abc.MutableSequence`, `tuple` [^2]
    * `set`, `collections.abc.Set`, `collections.abc.MutableSet` [^2]
    * `dict`, `collections.abc.Mapping`, `collections.abc.MutableMapping` [^2]
    * [`frozenset`](https://docs.python.org/3/library/stdtypes.html#frozenset) [^3]
    * [`defaultdict`](https://docs.python.org/3/library/collections.html#collections.defaultdict) [^4]
* [`typing.Optional`](https://docs.python.org/3/library/typing.html#typing.Optional)[^5]
* [`typing.Union`](https://docs.python.org/3/library/typing.html#typing.Union) [^6] [^7] [^8]
* [`@dataclass`](https://docs.python.org/3/library/dataclasses.html) を用いたユーザ定義クラス [^9] [^10]
* [`typing.NewType`](https://docs.python.org/3/library/typing.html#newtype) を用いたプリミティブ型 [^11]
* [`typing.Any`](https://docs.python.org/3/library/typing.html#the-any-type) [^12]
* [`typing.Literal`](https://docs.python.org/3/library/typing.html#typing.Literal) [^13]
* [`typing.Generic`](https://docs.python.org/3/library/typing.html#user-defined-generic-types) [^14]
* [`typing.ClassVar`](https://docs.python.org/3/library/typing.html#typing.ClassVar) [^15]
* [`typing.InitVar`](https://docs.python.org/3/library/dataclasses.html#init-only-variables) [^16]
* [`Enum`](https://docs.python.org/3/library/enum.html#enum.Enum) および [`IntEnum`](https://docs.python.org/3/library/enum.html#enum.IntEnum) [^17]
* 標準ライブラリ
    * [`pathlib.Path`](https://docs.python.org/3/library/pathlib.html) [^18]
    * [`decimal.Decimal`](https://docs.python.org/3/library/decimal.html) [^19]
    * [`uuid.UUID`](https://docs.python.org/3/library/uuid.html) [^20]
    * [`datetime.date`](https://docs.python.org/3/library/datetime.html#date-objects)、[`datetime.time`](https://docs.python.org/3/library/datetime.html#time-objects)、[`datetime.datetime`](https://docs.python.org/3/library/datetime.html#datetime-objects) [^21]
    * [`ipaddress`](https://docs.python.org/3/library/ipaddress.html) [^22]
* PyPIライブラリ
    * [`numpy`](https://github.com/numpy/numpy) データ型 [^23]
    * 宣言的データクラスマッピングを用いた [`SQLAlchemy`](https://github.com/sqlalchemy/sqlalchemy)（実験的）[^24]

このように複雑なクラスを記述することができます。
```python
@serde
class bar:
    i: int

@serde
class Foo:
    a: int
    b: list[str]
    c: tuple[int, float, str, bool]
    d: dict[str, list[tuple[str, int]]]
    e: str | None
    f: Bar
```

## Numpy

上記のすべての（デ）シリアライズ方法は、`numpy`追加パッケージを使用することで、ほとんどのnumpyデータ型を透過的に扱うことができます。

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

## SQLAlchemy宣言的データクラスマッピング（実験的）
SQLAlchemy宣言的データクラスマッピング統合の実験的サポートが追加されましたが、`@serde(type_check=strict)`や`serde.field()`などの特定の機能は現在サポートされていません。

実験的な機能に依存する場合、本番環境での使用には注意が必要です。  
コードを徹底的にテストし、潜在的な制限や予期せぬ動作に注意することを推奨します。

## 新しい型のサポートが必要ですか？

標準ライブラリに現在サポートされていない型を使用する必要がある場合は、Githubでissueを作成してリクエストしてください。  
なお、サードパーティのPythonパッケージの型については、numpyのような人気のあるパッケージの型を除き、pyserdeをできるだけシンプルに保つためにサポートする予定はありません。  
カスタムクラスやフィールドシリアライザの使用を推奨します。

[^1]: [examples/simple.py](https://github.com/yukinarit/pyserde/blob/main/examples/simple.py) を参照

[^2]: [examples/collection.py](https://github.com/yukinarit/pyserde/blob/main/examples/collection.py) を参照

[^3]: [examples/frozen_set.py](https://github.com/yukinarit/pyserde/blob/main/examples/frozen_set.py) を参照

[^4]: [examples/default_dict.py](https://github.com/yukinarit/pyserde/blob/main/examples/default_dict.py) を参照

[^5]: [examples/union.py](https://github.com/yukinarit/pyserde/blob/main/examples/union.py) を参照

[^6]: [examples/union.py](https://github.com/yukinarit/pyserde/blob/main/examples/union.py) を参照

[^7]: [examples/union_operator.py](https://github.com/yukinarit/pyserde/blob/main/examples/union_operator.py) を参照

[^8]: [examples/union_tagging.py](https://github.com/yukinarit/pyserde/blob/main/examples/union_tagging.py) を参照

[^9]: [examples/simple.py](https://github.com/yukinarit/pyserde/blob/main/examples/simple.py) を参照

[^10]: [examples/nested.py](https://github.com/yukinarit/pyserde/blob/main/examples/nested.py) を参照

[^11]: [examples/newtype.py](https://github.com/yukinarit/pyserde/blob/main/examples/newtype.py) を参照

[^12]: [examples/any.py](https://github.com/yukinarit/pyserde/blob/main/examples/any.py) を参照

[^13]: [examples/literal.py](https://github.com/yukinarit/pyserde/blob/main/examples/literal.py) を参照

[^14]: [examples/generics.py](https://github.com/yukinarit/pyserde/blob/main/examples/generics.py) を参照

[^15]: [examples/class_var.py](https://github.com/yukinarit/pyserde/blob/main/examples/class_var.py) を参照

[^16]: [examples/init_var.py](https://github.com/yukinarit/pyserde/blob/main/examples/init_var.py) を参照

[^17]: [examples/enum34.py](https://github.com/yukinarit/pyserde/blob/main/examples/enum34.py) を参照

[^18]: [examples/type_pathlib.py](https://github.com/yukinarit/pyserde/blob/main/examples/type_pathlib.py) を参照

[^19]: [examples/type_decimal.py](https://github.com/yukinarit/pyserde/blob/main/examples/type_decimal.py) を参照

[^20]: [examples/type_uuid.py](https://github.com/yukinarit/pyserde/blob/main/examples/type_uuid.py) を参照

[^21]: [examples/type_datetime.py](https://github.com/yukinarit/pyserde/blob/main/examples/type_datetime.py) を参照

[^22]: [examples/type_ipaddress.py](https://github.com/yukinarit/pyserde/blob/main/examples/type_ipaddress.py) を参照

[^23]: [examples/type_numpy.py](https://github.com/yukinarit/pyserde/blob/main/examples/type_numpy.py) を参照

[^24]: [examples/type_sqlalchemy.py](https://github.com/yukinarit/pyserde/blob/main/examples/type_sqlalchemy.py) を参照
