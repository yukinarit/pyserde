# Rename

In case you want to use a keyword as field such as `class`, you can use `serde_rename` field attribute.

```python
@serde
@dataclass
class Foo:
    class_name: str = field(metadata={'serde_rename': 'class'})

print(to_json(Foo(class_name='Foo')))
```

Output json is having `class` instead of `class_name`.

```json
{"class": "Foo"}
```

For complete example, please see [examples/rename.py](https://github.com/yukinarit/pyserde/blob/master/examples/rename.py)
