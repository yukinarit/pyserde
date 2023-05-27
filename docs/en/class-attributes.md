# Class Attributes

Class attributes can be specified as arguments in the `serialize`/`deserialize` decorators in order to customize the (de)serialization behaviour of the class entirely. If you want to customize a field, please consider using [Field Attributes](field-attributes.md).

## **`rename_all`**

`rename_all` can converts field names into the specified string case. The following example converts camel case field names into snake case names. Case coversion depends on [python-casefy](https://github.com/dmlls/python-casefy). You can find the list of supported cases in [the python-casefy's docs](https://dmlls.github.io/python-casefy/api.html).

```python
@serde(rename_all = 'camelcase')
@dataclass
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
> @dataclass
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

## **`tagging`**

New in v0.7.0. See [Union](union.md).

## **`serializer`** / **`deserializer`**

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
@dataclass
class Foo:
    a: datetime
```

See [examples/custom_class_serializer.py](https://github.com/yukinarit/pyserde/blob/main/examples/custom_class_serializer.py) for complete example.

## **`type_check`**

New in v0.9.0. See [Type Check](#type-check.md).

## **`serialize_class_var`**

New in v0.9.8. Since `dataclasses.fields` doesn't include a class variable [^1], pyserde doesn't serialize class variable as default. This option allows a field of `typing.ClassVar` to be serialized.

```python
@serde(serialize_class_var=True)
@dataclass
class Foo:
    a: ClassVar[int] = 10
```

See [examples/class_var.py](https://github.com/yukinarit/pyserde/blob/main/examples/class_var.py) for complete example.

[^1]: https://docs.python.org/3/library/dataclasses.html#dataclasses.fields
