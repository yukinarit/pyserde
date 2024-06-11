# Introduction

`pyserde`は[dataclasses](https://docs.python.org/3/library/dataclasses.html)ベースのシンプルで強力なシリアライゼーションライブラリで、クラスをJSONやYAML等の様々なデータフォーマットに簡単に効率的に変換可能になります。

クラスに`@serde`デコレータを付け、[PEP484](https://peps.python.org/pep-0484/)形式でフィールドに型アノテーションを付けます。

```python
from serde import serde

@serde
class Foo:
    i: int
    s: str
    f: float
    b: bool
```

すると、`Foo`クラスは以下のようにJSONにシリアライズ出来るようになります。

```python
>>> from serde.json import to_json
>>> to_json(Foo(i=10, s='foo', f=100.0, b=True))
'{"i":10,"s":"foo","f":100.0,"b":true}'
```

また、JSONから`Foo`クラスにデシリアライズも出来るようになります。
```python
>>> from serde.json import from_json
>>> from_json(Foo, '{"i": 10, "s": "foo", "f": 100.0, "b": true}')
Foo(i=10, s='foo', f=100.0, b=True)
```

## Next Steps

* [Getting started](getting-started.md)
* [API Reference](https://yukinarit.github.io/pyserde/api/serde.html)
* [Examples](https://github.com/yukinarit/pyserde/tree/main/examples)
* [FAQ](faq.md)
