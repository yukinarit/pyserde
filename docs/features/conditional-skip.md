# Conditional Skip

If you conditionally skip some fields, you can pass function or lambda in `serde_skip_if`.

```python
@serde
class World:
    player: str
    buddy: str = field(default='', metadata={'serde_skip_if': lambda v: v == 'Pikachu'})

world = World('satoshi', 'Pikachu')
print(to_json(world))

world = World('green', 'Charmander')
print(to_json(world))
```

As you can see below, field is skipped in serialization if `buddy` is "Pikachu".

```json
{"player": "satoshi"}
{"player": "green", "buddy": "Charmander"}
```

For complete example, please see [examples/skip.py](https://github.com/yukinarit/pyserde/blob/master/examples/skip.py)
