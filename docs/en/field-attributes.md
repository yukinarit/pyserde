# Field Attributes

Field attributes are options to customize (de)serialization behaviour for a field of a dataclass.

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
    b: str = dataclasses.field(metadata={"serde_rename"="B"})
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

See [examples/skip.py](https://github.com/yukinarit/pyserde/blob/main/examples/skip.py) for the complete example.

### **`skip_if`**

`skip` is used to skip (de)serialization of the field if the predicate function returns `True`.

```python
@serde
class World:
    buddy: str = field(default='', skip_if=lambda v: v == 'Pikachu')
```

See [examples/skip.py](https://github.com/yukinarit/pyserde/blob/main/examples/skip.py) for the complete example.

### **`skip_if_false`**

`skip` is used to skip (de)serialization of the field if the field evaluates to `False`. For example, this code skip (de)serializing if `enemies` is empty.

```python
@serde
class World:
    enemies: list[str] = field(default_factory=list, skip_if_false=True)
```

See [examples/skip.py](https://github.com/yukinarit/pyserde/blob/main/examples/skip.py) for the complete example.

### **`skip_if_default`**

`skip` is used to skip (de)serialization of the field if the field is equivalent to its default value. For example, this code skip (de)serializing if `town` is `Masara Town`.

```python
@serde
class World:
    town: str = field(default='Masara Town', skip_if_default=True)
```

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

You can flatten the fields of the nested structure.

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
