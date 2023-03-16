# Rename

In case you want to use a keyword as field such as `class`, you can use `rename` field attribute. If you want to have multiple aliases, you can use [alias](alias.md).

```python
@serde
@dataclass
class Foo:
    class_name: str = field(rename='class')

print(to_json(Foo(class_name='Foo')))
```

Output json is having `class` instead of `class_name`.

```json
{"class": "Foo"}
```

For complete example, please see [examples/rename.py](https://github.com/yukinarit/pyserde/blob/main/examples/rename.py)
