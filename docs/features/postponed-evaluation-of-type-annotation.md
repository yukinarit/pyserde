# Postponed evaluation of type annotation

[PEP563](https://www.python.org/dev/peps/pep-0563/) Postponed evaluation of type annotation is supported.

```python
from __future__ import annotations
from serde import serde
from dataclasses import dataclass

@serde
@dataclass
class Foo:
    i: int
    s: str
    f: float
    b: bool

    def foo(self, cls: Foo):  # You can use "Foo" type before it's defined.
        print('foo')
```

For complete example, please see [examples/lazy_type_evaluation.py](https://github.com/yukinarit/pyserde/blob/master/examples/lazy_type_evaluation.py)
