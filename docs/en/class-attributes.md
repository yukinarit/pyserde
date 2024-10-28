# Class Attributes

Class attributes can be specified as arguments in the `serialize`/`deserialize` decorators in order to customize the (de)serialization behaviour of the class entirely. If you want to customize a field, please consider using [Field Attributes](field-attributes.md).

## Attributes offered by dataclasses

### **`frozen`**

dataclass `frozen` class attribute works as expected.

### **`kw_only`**

New in v0.12.2. dataclass `kw_only` class attribute works as expected.

```python
@serde
@dataclass(kw_only=True)
class Foo:
    i: int
    s: str
    f: float
    b: bool
```

See [examples/kw_only.py](https://github.com/yukinarit/pyserde/blob/main/examples/kw_only.py) for the complete example.

## Attributes offered by pyserde

### **`rename_all`**

`rename_all` can converts field names into the specified string case. The following example converts camel case field names into snake case names. Case coversion depends on [python-casefy](https://github.com/dmlls/python-casefy). You can find the list of supported cases in [the python-casefy's docs](https://dmlls.github.io/python-casefy/api.html).

```python
@serde(rename_all = 'camelcase')
class Foo:
    int_field: int
    str_field: str

f = Foo(int_field=10, str_field='foo')
print(to_json(f))
```

"int_field" is converted to "intField" and "str_field" is converted to "strField".

```json
{"intField": 10, "strField": "foo"}
```

> **NOTE:** If `rename_all` class attribute and `rename` field attribute are used at the same time, `rename` will be prioritized.
>
> ```python
> @serde(rename_all = 'camelcase')
> class Foo:
>     int_field: int
>     str_field: str = field(rename='str-field')
>
> f = Foo(int_field=10, str_field='foo')
> print(to_json(f))
> ```
> The above code prints
> ```
> {"intField": 10, "str-field": "foo"}
> ```

See [examples/rename_all.py](https://github.com/yukinarit/pyserde/blob/main/examples/rename_all.py) for the complete example.

### **`tagging`**

New in v0.7.0. See [Union](union.md).

### **`class_serializer`** / **`class_deserializer`**

If you want to use a custom (de)serializer at class level, you can pass your (de)serializer object in `class_serializer` and `class_deserializer` class attributes. Class custom (de)serializer depends on a python library [plum](https://github.com/beartype/plum) which allows multiple method overloading like C++. With plum, you can write robust custom (de)serializer in a quite neat way.

```python
class MySerializer:
    @dispatch
    def serialize(self, value: datetime) -> str:
        return value.strftime("%d/%m/%y")

class MyDeserializer:
    @dispatch
    def deserialize(self, cls: Type[datetime], value: Any) -> datetime:
        return datetime.strptime(value, "%d/%m/%y")

@serde(class_serializer=MySerializer(), class_deserializer=MyDeserializer())
class Foo:
    v: datetime
```

One big difference from legacy `serializer` and `deserializer` is the fact that new `class_serializer` and `class_deserializer` are more deeply integrated at the pyserde's code generator level. You no longer need to handle Optional, List and Nested dataclass by yourself. Custom class (de)serializer will be used at all level of (de)serialization so you can extend pyserde to support third party types just like builtin types.

Also,
* If both field and class serializer specified, field serializer is prioritized
* If both legacy and new class serializer specified, new class serializer is prioritized

> 💡 Tip: If you implements multiple `serialize` methods, you will receive "Redefinition of unused `serialize`" warning from type checker. In such case, try using `plum.overload` and `plum.dispatch` to workaround it. See [plum's documentation](https://beartype.github.io/plum/integration.html) for more information.
>
> ```python
> from plum import dispatch, overload
> 
> class Serializer:
>    # use @overload
>    @overload
>    def serialize(self, value: int) -> Any:
>        return str(value)
>
>    # use @overload
>    @overload
>    def serialize(self, value: float) -> Any:
>        return int(value)
>
>    # Add method time and make sure to add @dispatch. Plum will do all the magic to erase warnings from type checker.
>    @dispatch
>    def serialize(self, value: Any) -> Any:
>        ...
> ```

See [examples/custom_class_serializer.py](https://github.com/yukinarit/pyserde/blob/main/examples/custom_class_serializer.py) for complete example.

New in v0.13.0.

### **`serializer`** / **`deserializer`**

> **NOTE:** Deprecated since v0.13.0. Consider using `class_serializer` and `class_deserializer`.

If you want to use a custom (de)serializer at class level, you can pass your (de)serializer methods n `serializer` and `deserializer` class attributes.

```python
def serializer(cls, o):
    if cls is datetime:
        return o.strftime('%d/%m/%y')
    else:
        raise SerdeSkip()

def deserializer(cls, o):
    if cls is datetime:
        return datetime.strptime(o, '%d/%m/%y')
    else:
        raise SerdeSkip()

@serde(serializer=serializer, deserializer=deserializer)
class Foo:
    a: datetime
```

See [examples/custom_legacy_class_serializer.py](https://github.com/yukinarit/pyserde/blob/main/examples/custom_legacy_class_serializer.py) for complete example.

### **`type_check`**

New in v0.9.0. See [Type Check](type-check.md).

### **`serialize_class_var`**

New in v0.9.8. Since `dataclasses.fields` doesn't include a class variable [^1], pyserde doesn't serialize class variable as default. This option allows a field of `typing.ClassVar` to be serialized.

```python
@serde(serialize_class_var=True)
class Foo:
    a: ClassVar[int] = 10
```

See [examples/class_var.py](https://github.com/yukinarit/pyserde/blob/main/examples/class_var.py) for complete example.

[^1]: [dataclasses.fields](https://docs.python.org/3/library/dataclasses.html#dataclasses.fields)

### **`deny_unknown_fields`**

New in v0.22.0, the `deny_unknown_fields` option in the pyserde decorator allows you to enforce strict field validation during deserialization. When this option is enabled, any fields in the input data that are not defined in the target class will cause deserialization to fail with a `SerdeError`.

Consider the following example:
```python
@serde(deny_unknown_fields=True)
class Foo:
    a: int
    b: str
```

With `deny_unknown_fields=True`, attempting to deserialize data containing fields beyond those defined (a and b in this case) will raise an error. For instance:
```
from_json(Foo, '{"a": 10, "b": "foo", "c": 100.0, "d": true}')
```
This will raise a `SerdeError` since fields c and d are not recognized members of Foo.

See [examples/deny_unknown_fields.py](https://github.com/yukinarit/pyserde/blob/main/examples/deny_unknown_fields.py) for complete example.
