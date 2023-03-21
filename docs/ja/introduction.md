# Introduction

`pyserde`は[dataclasses](https://docs.python.org/3/library/dataclasses.html)をベースにした強力なシリアライゼーションのライブラリです。 `@serde`デコレータをクラスに付けるだけで様々なデータフォーマットにシリアライズ・デシリアライズが可能になります。

```python
@serde
@dataclass
class Foo:
    i: int
    s: str
    f: float
    b: bool
```

`Foo`のオブジェクトをJSONにシリアライズしてみます。

```python
>>> to_json(Foo(i=10, s='foo', f=100.0, b=True))
'{"i":10,"s":"foo","f":100.0,"b":true}'
```

JSONから`Foo`にデシリアライズしてみます。
```python
>>> from_json(Foo, '{"i": 10, "s": "foo", "f": 100.0, "b": true}')
Foo(i=10, s='foo', f=100.0, b=True)
```
