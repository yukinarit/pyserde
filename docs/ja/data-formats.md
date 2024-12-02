# Data Formats

pyserdeは、`dict`、`tuple`、`JSON`、`YAML`、`TOML`、`MsgPack`、`Pickle` などのさまざまなデータ形式をシリアライズおよびデシリアライズできます。  
各APIは追加のキーワード引数を取ることができ、これらの引数はpyserdeで使用されるベースパッケージへと渡されます。

例えば、YAMLでフィールドの順序を保持したい場合、`serde.yaml.to_yaml`に`sort_key=True`を渡すことができます。

```python
serde.yaml.to_yaml(foo, sort_key=True)
```

`sort_key=True`は[yaml.safedump](https://github.com/yukinarit/pyserde/blob/a9f44d52d109144a4c3bb93965f831e91d13960b/serde/yaml.py#L18)に渡されます。

## dict

```python
>>> from serde import to_dict, from_dict

>>> to_dict(Foo(i=10, s='foo', f=100.0, b=True))
{"i": 10, "s": "foo", "f": 100.0, "b": True}

>>> from_dict(Foo, {"i": 10, "s": "foo", "f": 100.0, "b": True})
Foo(i=10, s='foo', f=100.0, b=True)
```

詳細は[serde.to_dict](https://yukinarit.github.io/pyserde/api/serde/se.html#to_dict) / [serde.from_dict](https://yukinarit.github.io/pyserde/api/serde/de.html#from_dict)をご覧ください。

## tuple

```python
>>> from serde import to_tuple, from_tuple

>>> to_tuple(Foo(i=10, s='foo', f=100.0, b=True))
(10, 'foo', 100.0, True)

>>> from_tuple(Foo, (10, 'foo', 100.0, True))
Foo(i=10, s='foo', f=100.0, b=True)
```

詳細は[serde.to_tuple](https://yukinarit.github.io/pyserde/api/serde/se.html#to_tuple) / [serde.from_tuple](https://yukinarit.github.io/pyserde/api/serde/de.html#from_tuple)をご覧ください。

## JSON

```python
>>> from serde.json import to_json, from_json

>>> to_json(Foo(i=10, s='foo', f=100.0, b=True))
'{"i":10,"s":"foo","f":100.0,"b":true}'

>>> from_json(Foo, '{"i": 10, "s": "foo", "f": 100.0, "b": true}')
Foo(i=10, s='foo', f=100.0, b=True)
```

詳細は[serde.json.to_json](https://yukinarit.github.io/pyserde/api/serde/json.html#to_json) / [serde.json.from_json](https://yukinarit.github.io/pyserde/api/serde/json.html#from_json)をご覧ください。

## Yaml

```python
>>> from serde.yaml import from_yaml, to_yaml

>>> to_yaml(Foo(i=10, s='foo', f=100.0, b=True))
b: true
f: 100.0
i: 10
s: foo

>>> from_yaml(Foo, 'b: true\nf: 100.0\ni: 10\ns: foo')
Foo(i=10, s='foo', f=100.0, b=True)
```

詳細は[serde.yaml.to_yaml](https://yukinarit.github.io/pyserde/api/serde/yaml.html#to_yaml) / [serde.yaml.from_yaml](https://yukinarit.github.io/pyserde/api/serde/yaml.html#from_yaml)をご覧ください。

## Toml

```python
>>> from serde.toml from_toml, to_toml

>>> to_toml(Foo(i=10, s='foo', f=100.0, b=True))
i = 10
s = "foo"
f = 100.0
b = true

>>> from_toml(Foo, 'i = 10\ns = "foo"\nf = 100.0\n

b = true')
Foo(i=10, s='foo', f=100.0, b=True)
```

詳細は[serde.toml.to_toml](https://yukinarit.github.io/pyserde/api/serde/toml.html#to_toml) / [serde.toml.from_toml](https://yukinarit.github.io/pyserde/api/serde/toml.html#from_toml)をご覧ください。

## MsgPack

```python
>>> from serde.msgpack import from_msgpack, to_msgpack

>>> to_msgpack(Foo(i=10, s='foo', f=100.0, b=True))
b'\x84\xa1i\n\xa1s\xa3foo\xa1f\xcb@Y\x00\x00\x00\x00\x00\x00\xa1b\xc3'

>>> from_msgpack(Foo, b'\x84\xa1i\n\xa1s\xa3foo\xa1f\xcb@Y\x00\x00\x00\x00\x00\x00\xa1b\xc3')
Foo(i=10, s='foo', f=100.0, b=True)
```

詳細は[serde.msgpack.to_msgpack](https://yukinarit.github.io/pyserde/api/serde/msgpack.html#to_msgpack) / [serde.msgpack.from_msgpack](https://yukinarit.github.io/pyserde/api/serde/msgpack.html#from_msgpack)をご覧ください。

## Pickle

v0.9.6で新しく追加されました

```python
>>> from serde.pickle import from_pickle, to_pickle

>>> to_pickle(Foo(i=10, s='foo', f=100.0, b=True))
b"\x80\x04\x95'\x00\x00\x00\x00\x00\x00\x00}\x94(\x8c\x01i\x94K\n\x8c\x01s\x94\x8c\x03foo\x94\x8c\x01f\x94G@Y\x00\x00\x00\x00\x00\x00\x8c\x01b\x94\x88u."

>>> from_pickle(Foo, b"\x80\x04\x95'\x00\x00\x00\x00\x00\x00\x00}\x94(\x8c\x01i\x94K\n\x8c\x01s\x94\x8c\x03foo\x94\x8c\x01f\x94G@Y\x00\x00\x00\x00\x00\x00\x8c\x01b\x94\x88u.")
Foo(i=10, s='foo', f=100.0, b=True)
```

詳細は[serde.pickle.to_pickle](https://yukinarit.github.io/pyserde/api/serde/pickle.html#to_pickle) / [serde.pickle.from_pickle](https://yukinarit.github.io/pyserde/api/serde/pickle.html#from_pickle)をご覧ください。

## 新しいデータ形式のサポートが必要ですか？

pyserde をできるだけシンプルに保つため、XML のようなデータフォーマットをサポートする予定はありません。  
新しいデータ形式のサポートが必要な場合は、別のPythonパッケージを作成することをお勧めします。  
データ形式がdictやtupleに変換可能であれば、シリアライズ/デシリアライズAPIの実装はそれほど難しくありません。  
実装方法を知りたい場合は、[YAMLの実装](https://github.com/yukinarit/pyserde/blob/main/serde/yaml.py)をご覧ください。
