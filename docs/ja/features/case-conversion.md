# Case Conversion

Converting `snake_case` fields into supported case styles e.g. `camelCase` and `kebab-case`.

```python
@serde(rename_all = 'camelcase')
@dataclass
class Foo:
    int_field: int
    str_field: str

f = Foo(int_field=10, str_field='foo')
print(to_json(f))
```

Here, the output is all `camelCase`.

```json
{"intField": 10, "strField": "foo"}
```
