# Attributes

## Class attributes

Class attributes can be specified as arguments in the `serialize`/`deserialize` decorator in order to customize the deserialization behaviour of the class entirely.

For more information about available attirbutes, please see [serialize](https://yukinarit.github.io/pyserde/api/serde/se.html#serialize)/[deserialize](https://yukinarit.github.io/pyserde/api/serde/de.html#deserialize) API docs.

## Field attributes

Field attributes are options to customize (de)serialization behaviour specific to field. `pyserde` provides two way to specify field attributes. 

### `serde.field`

You can specify field attributes as keyword argument in `serde.field`. See [serde.core.Field](https://yukinarit.github.io/pyserde/api/serde/core.html#Field) for available field attributes. This is recommended way since pyserde v0.6. Use `dataclasses.field` below if you are using pyserde < v0.6.

```python
from dataclasses import dataclass
from serde import field, serde

@serde
@dataclass
class Foo:
    class_name: str = field(rename='class')
```

### `dataclasses.field`

Field attributes can be specified through metadata of `dataclasses.field`. dataclasses metadata is a container where users can pass arbitrary key and value. The above example can be written using `dataclasses.field` instead of `serde.field`.

```python
from dataclasses import field
from serde import serde

@serde
class Foo:
    class_name: str = field(metadata={'serde_rename': 'class'})
```