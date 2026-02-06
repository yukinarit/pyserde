# Field Attributes

Field attributes are options to customize (de)serialization behaviour for a field of a dataclass. Use them when you want different wire formats, optional behavior, or custom logic for specific fields.

## Attributes offered by dataclasses

### **`default`** / **`default_factory`**

`default` and `default_factory` work as expected. If a field has `default` or `default_factory` attribute, it behaves like an optional field. If the field is found in the data, the value is fetched from the data and set in the deserialized object. If the field is not found in the data, the specified default value is set in the deserialized object.

```python
class Foo:
    a: int = 10
    b: int = field(default=10)  # same as field "a"
    c: dict[str, int] = field(default_factory=dict)

print(from_dict(Foo, {}))  # prints Foo(a=10, b=10, c={})
```

See [examples/default.py](https://github.com/yukinarit/pyserde/blob/main/examples/default.py) for the complete example.

### **`ClassVar`**

`dataclasses.ClassVar` is a class variable for the dataclasses. Since dataclass treats ClassVar as pseudo-field and `dataclasses.field` doesn't pick ClassVar, pyserde doesn't (de)serialize ClassVar fields as a default behaviour. If you want to serialize ClassVar fields, consider using [serialize_class_var](class-attributes.md#serialize_class_var) class attribute.

See [examples/class_var.py](https://github.com/yukinarit/pyserde/blob/main/examples/class_var.py) for the complete example.

## Attributes offered by pyserde

Field attributes can be specified through `serde.field` or `dataclasses.field`. We recommend to use `serde.field` because it's shorter and type check works.
Here is an example specifying `rename` attribute in both `serde.field` and `dataclasses.field`.

```python
@serde.serde
class Foo:
    a: str = serde.field(rename="A")
    b: str = dataclasses.field(metadata={"serde_rename": "B"})
```

### **`rename`**

`rename` is used to rename field name during (de)serialization. This attribute is convenient when you want to use a python keyword in field name. For example, this code renames field name `id` to `ID`.

```python
@serde
class Foo:
    id: int = field(rename="ID")
```

See [examples/rename.py](https://github.com/yukinarit/pyserde/blob/main/examples/rename.py) for the complete example.

### **`skip`**

`skip` is used to skip (de)serialization of the field with this attribute.

```python
@serde
class Resource:
    name: str
    hash: str
    metadata: dict[str, str] = field(default_factory=dict, skip=True)
```

See [examples/skip.py](https://github.com/yukinarit/pyserde/blob/main/examples/skip.py) and [examples/skip_if_default_class.py](https://github.com/yukinarit/pyserde/blob/main/examples/skip_if_default_class.py) for complete examples.

### **`skip_serializing`**

`skip_serializing` omits the field only when serializing. The field is still accepted on input.

```python
@serde
class Credentials:
    user: str
    token: str = field(skip_serializing=True)
```

See [examples/skip_serializing_deserializing.py](https://github.com/yukinarit/pyserde/blob/main/examples/skip_serializing_deserializing.py) for the complete example.

### **`skip_deserializing`**

`skip_deserializing` ignores incoming data for the field and keeps its default/default_factory value. A default is required when the field participates in `__init__`.

```python
@serde
class Profile:
    username: str
    session_id: str = field(default="generated", skip_deserializing=True)
```

See [examples/skip_serializing_deserializing.py](https://github.com/yukinarit/pyserde/blob/main/examples/skip_serializing_deserializing.py) for the complete example.

### **`skip_if`**

`skip_if` is used to skip (de)serialization of the field if the predicate function returns `True`.

```python
@serde
class World:
    buddy: str = field(default='', skip_if=lambda v: v == 'Pikachu')
```

See [Class Attributes: skip_if_default](class-attributes.md#skip_if_default) for the class-level toggle, and [examples/skip.py](https://github.com/yukinarit/pyserde/blob/main/examples/skip.py) plus [examples/skip_if_default_class.py](https://github.com/yukinarit/pyserde/blob/main/examples/skip_if_default_class.py) for the complete examples.

!!! note
    `skip`, `skip_if`, `skip_if_false`, `skip_if_none`, and `skip_if_default` apply to both serialization and deserialization. Use `skip_serializing` / `skip_deserializing` to make direction-specific choices.

### **`skip_if_false`**

`skip` is used to skip (de)serialization of the field if the field evaluates to `False`. For example, this code skip (de)serializing if `enemies` is empty.

```python
@serde
class World:
    enemies: list[str] = field(default_factory=list, skip_if_false=True)
```

See [examples/skip.py](https://github.com/yukinarit/pyserde/blob/main/examples/skip.py) for the complete example.

### **`skip_if_none`**

`skip_if_none` skips (de)serialization of the field when its value is `None`.

```python
@serde
class Profile:
    nickname: str | None = field(default=None, skip_if_none=True)
```

You can also enable this for all fields in a class; see [Class Attributes: skip_if_none](class-attributes.md#skip_if_none).
See [examples/skip_if_none.py](https://github.com/yukinarit/pyserde/blob/main/examples/skip_if_none.py) for a runnable example.

### **`skip_if_default`**

`skip_if_default` skips (de)serialization of the field when its value equals the default.

```python
@serde
class World:
    town: str = field(default='Masara Town', skip_if_default=True)
```

You can also enable it for every field in a class at once:

```python
@serde(skip_if_default=True)
class Settings:
    theme: str = "light"
    retries: int = 3
```

Field-level values still override the class setting; set `skip_if_default=False` on a field to keep it even when class-level skipping is enabled.

See [examples/skip.py](https://github.com/yukinarit/pyserde/blob/main/examples/skip.py) for the complete example.

### **`alias`**

You can set aliases for field names. Alias only works for deserialization.

```python
@serde
class Foo:
    a: str = field(alias=["b", "c"])
```

`Foo` can be deserialized from either `{"a": "..."}`, `{"b": "..."}` or `{"c": "..."}`.

See [examples/alias.py](https://github.com/yukinarit/pyserde/blob/main/examples/alias.py) for complete example.

## **`serializer`**/**`deserializer`**

Sometimes you want to customize (de)serializer for a particular field, such as
* You want to serialize datetime into a different format
* You want to serialize a type in a third party package

In the following example, field `a` is serialized into `"2021-01-01T00:00:00"` by the default serializer for `datetime`, whereas field `b` is serialized into `"01/01/21"` by the custom serializer.

```python
@serde
class Foo:
    a: datetime
    b: datetime = field(serializer=lambda x: x.strftime('%d/%m/%y'), deserializer=lambda x: datetime.strptime(x, '%d/%m/%y'))
```

See [examples/custom_field_serializer.py](https://github.com/yukinarit/pyserde/blob/main/examples/custom_field_serializer.py) for the complete example.

## **`flatten`**

The `flatten` attribute can be used in two ways:

### Flatten nested dataclass

You can flatten the fields of the nested dataclass structure.

```python
@serde
class Bar:
    c: float
    d: bool

@serde
class Foo:
    a: int
    b: str
    bar: Bar = field(flatten=True)
```

Bar's c, d fields are deserialized as if they are defined in Foo. So you will get `{"a":10,"b":"foo","c":100.0,"d":true}` if you serialize `Foo` into JSON.

See [examples/flatten.py](https://github.com/yukinarit/pyserde/blob/main/examples/flatten.py) for complete example.

### Capture additional fields with dict

You can use `dict[str, Any]` or bare `dict` with `flatten=True` to capture all unknown/extra fields during deserialization, similar to Rust serde's `#[serde(flatten)]` on `HashMap<String, Value>`.

```python
@serde
class User:
    id: int
    name: str
    extra: dict[str, Any] = field(flatten=True, default_factory=dict)

# Deserialization - extra fields captured
user = from_json(User, '{"id": 1, "name": "Alice", "role": "admin", "active": true}')
# user.extra == {"role": "admin", "active": True}

# Serialization - extra fields merged back
user2 = User(id=2, name="Bob", extra={"department": "Engineering"})
to_json(user2)  # '{"id": 2, "name": "Bob", "department": "Engineering"}'
```

**Key features:**
- During deserialization, any fields not matching declared fields are captured in the dict
- During serialization, the dict contents are merged into the output (declared fields take precedence)
- Works with all data formats (JSON, YAML, TOML, MessagePack, etc.)
- Can be combined with flattened dataclass fields

See [examples/flatten_dict.py](https://github.com/yukinarit/pyserde/blob/main/examples/flatten_dict.py) for complete example.
