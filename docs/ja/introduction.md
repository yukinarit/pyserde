# Introduction

`pyserde`は[dataclasses](https://docs.python.org/3/library/dataclasses.html)ベースのシンプルで強力なシリアライゼーションライブラリです。

クラスに`@serde`デコレータを付けるだけで、クラスを様々なデータフォーマットに変換可能になります。

```python
@serde
class Foo:
    i: int
    s: str
    f: float
    b: bool
```

`Foo`クラスは以下のようにJSONにシリアライズ出来るようになります。

```python
>>> to_json(Foo(i=10, s='foo', f=100.0, b=True))
'{"i":10,"s":"foo","f":100.0,"b":true}'
```

また、JSONから`Foo`クラスにデシリアライズも出来るようになります。
```python
>>> from_json(Foo, '{"i": 10, "s": "foo", "f": 100.0, "b": true}')
Foo(i=10, s='foo', f=100.0, b=True)
```
