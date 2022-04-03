# Skip

You can skip serialization for a certain field, you can use `serde_skip`.

```python
@serde
@dataclass
class Resource:
    name: str
    hash: str
    metadata: Dict[str, str] = field(default_factory=dict, metadata={'serde_skip': True})

resources = [
    Resource("Stack Overflow", "hash1"),
    Resource("GitHub", "hash2", metadata={"headquarters": "San Francisco"}) ]
print(to_json(resources))
```

Here, `metadata` is not present in output json.

```json
[{"name": "Stack Overflow", "hash": "hash1"}, {"name": "GitHub", "hash": "hash2"}]
```

For complete example, please see [examples/skip.py](https://github.com/yukinarit/pyserde/blob/master/examples/skip.py)
