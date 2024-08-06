# Decorators

## `@serde`

`@serde` は `@serialize` と `@deserialize` デコレータのラッパーです。

以下のコードがあるとします。
```python
@serde
class Foo:
    ...
```

上記のコードは、以下のコードと同等です。

```python
@deserialize
@serialize
@dataclass
class Foo:
    ...
```

`@serde` デコレータは以下を行います。
* クラスに `@serialize` と `@deserialize` デコレータを追加します。
* クラスが `@dataclass` を持っていない場合、`@dataclass` デコレータを追加します。
* 両方の（デ）シリアライズ属性をデコレータに渡すことができます。
    * `serializer` 属性は `@deserialize` で無視され、`deserializer` 属性は `@serialize` で無視されます。

```python
@serde(serializer=serializer, deserializer=deserializer)
@dataclass
class Foo:
    ...
```

> **注記:** `@serde` は `@dataclass` デコレータなしで動作します。  
> これはserdeが `@dataclass` を自動的に検出し、宣言されたクラスに追加するからです。  
> しかし `@dataclass` を定義しない場合、mypy では `Too many arguments` または `Unexpected keyword argument` というエラーが発生します。これは [mypy の制限](https://mypy.readthedocs.io/en/stable/additional_features.html#caveats-known-issues)によるものです。
>
> ```python
> @serde
> class Foo:
>     ...
> ```
>
> しかし、PEP681に準拠した型チェッカー（例：pyright）を使用すると、pyserdeが [PEP681 dataclass_transform](https://peps.python.org/pep-0681/) をサポートしているため、型エラーは発生しません。

## `@serialize` と `@deserialize`

`@serialize` および `@deserialize` は内部的に `@serde` によって使用されます。  
以下に該当する場合、これら2つのデコレータを使用することを推奨します。
* シリアライズまたはデシリアライズの機能のみが必要な場合
* 以下のように異なるクラス属性を持つことを望む場合

```python
@deserialize(rename_all = "snakecase")
@serialize(rename_all = "camelcase")
class Foo:
    ...
```
上記に当てはまらない場合は `@serde` の使用を推奨します。

## `@serde` なしでクラスを（デ）シリアライズする

pyserdeは v0.10.0 以降、`@serde` なしでデータクラスを（デ）シリアライズできます。  
この機能は、外部ライブラリで宣言されたクラスを使用したい場合や、`@serde` デコレータが型チェッカーで機能しない場合に便利です。[この例](https://github.com/yukinarit/pyserde/blob/main/examples/plain_dataclass.py)を参照してください。

どのように動作するのでしょうか？  
それは非常に単純で、クラスが`@serde`デコレータを持っていない場合、pyserdeは `@serde` デコレータを追加します。  
最初のAPI呼び出しには時間がかかるかもしれませんが、生成されたコードは内部的にキャッシュされるため問題にはなりません。  

以下にサードパーティパッケージのクラスをデシリアライズする例を示します。

```python
@dataclass
class External:
    ...

to_dict(External()) # "@serde" なしで動作します
```

この場合、`rename_all` などのクラス属性を指定することはできません。  
外部のデータクラスにクラス属性を追加したい場合は、データクラスを拡張することでそれを行う方法があります。[この例](https://github.com/yukinarit/pyserde/blob/main/examples/plain_dataclass_class_attribute.py)を参照してください。

```python
@dataclass
class External:
    some_value: int

@serde(rename_all="kebabcase")
@dataclass
class Wrapper(External):
    pass
```

## 前方参照をどのように使用するか？

pyserdeは前方参照をサポートしています。  
ネストされたクラス名を文字列で置き換えると、pyserdeはネストされたクラスが定義された後にデコレータを探して評価します。

```python
from __future__ import annotations # annotationsをインポート

@dataclass
class Foo:
    i: int
    s: str
    bar: Bar  # "Bar" は後で宣言されていても指定できます

@serde
@dataclass
class Bar:
    f: float
    b: bool

# "Bar" が定義された後に pyserde デコレータを評価します
serde(Foo)
```

## PEP563 Annotationsによる遅延評価

pyserdeは [PEP563 Annotationsによる遅延評価](https://peps.python.org/pep-0563/)をサポートしています。

```python
from __future__ import annotations
from serde import serde

@serde
class Foo:
    i: int
    s: str
    f: float
    b: bool

    def foo(self, cls: Foo):  # 定義される前に "Foo" 型を使用できます
        print('foo')
```

完全な例については [examples/lazy_type_evaluation.py](https://github.com/yukinarit/pyserde/blob/main/examples/lazy_type_evaluation.py) を参照してください。
