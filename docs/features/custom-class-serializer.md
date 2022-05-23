# Custom class (de)serializer

If you want to provide (de)serializer at class level, you can pass your functions to `serializer` and `deserializer` class attributes.

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
    i: int
    dt1: datetime
    dt2: datetime
```

For complete example, please see [examples/custom_class_serializer.py](https://github.com/yukinarit/pyserde/blob/master/examples/custom_class_serializer.py)
