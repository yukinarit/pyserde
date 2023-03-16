# PEP604 Union operator

For python >= 3.10, you can use [PEP604](https://www.python.org/dev/peps/pep-0604/) Union operator `X | Y`.

```python
from dataclasses import dataclass
from serde import serde
from serde.json import from_json, to_json


@serde
@dataclass
class Bar:
    v: int


@serde
@dataclass
class Baz:
    v: float


@serde
@dataclass
class Foo:
    a: int | str
    b: dict[str, int] | list[int]
    c: Bar | Baz
```