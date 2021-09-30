# Supported data formats

## JSON

```python
from serde.json import from_json, to_json
print(to_json(f))
print(from_json(Foo, s))
```

## Yaml

```python
from serde.yaml import from_yaml, to_yaml
print(to_yaml(f))
print(from_yaml(Foo, s))
```

## Toml

```python
from serde.toml import from_toml, to_toml
print(to_toml(f))
print(from_toml(Foo, s))
```

## MsgPack

```python
from serde.msgpack import from_msgpack, to_msgpack
print(to_msgpack(f))
print(from_msgpack(Foo, s))
```
