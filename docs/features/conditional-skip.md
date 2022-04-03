# Conditional Skip

## `skip_if`

If you conditionally skip some fields, you can pass function or lambda in `skip_if`.

```python
@serde
@dataclass
class World:
    player: str
    buddy: str = field(default='', skip_if=lambda v: v == 'Pikachu')

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

## `skip_if_false`

`skip_if_false` is a shorthand of `skip_if=lambda v: not v`.

## `skip_if_default`

`skip_if_false` is a shorthand of `skip_if=lambda v: v == <default_value>`.

For complete example, please see [examples/skip.py](https://github.com/yukinarit/pyserde/blob/master/examples/skip.py)
