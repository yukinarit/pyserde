# Custom field (de)serializer

If you want to provide a custom function to override the default (de)serialization behaviour of a field, you can pass your functions to `serializer` and `deserializer` in `serde.field`.

```python
from dataclasses import dataclass
from serde import serde, field

@serde
@dataclass
class Foo:
    dt1: datetime
    dt2: datetime = field(
        serializer=lambda x: x.strftime('%d/%m/%y'), deserializer=lambda x: datetime.strptime(x, '%d/%m/%y')
    )
```
`dt1` in the example will serialized into `2021-01-01T00:00:00` because the pyserde's default (de)serializer for datetime is ISO 8601. `dt2` field in the example will be serialized into `01/01/21` by the custom field serializer.

For complete example, please see [examples/custom_field_serializer.py](https://github.com/yukinarit/pyserde/blob/master/examples/custom_field_serializer.py)
