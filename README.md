# pyserde

[![image](https://img.shields.io/pypi/pyversions/pyserde.svg)](https://pypi.org/project/requests/)
[![Build Status](https://travis-ci.org/yukinarit/pyserde.svg?branch=master)](https://travis-ci.org/yukinarit/pyserde)
[![Build status](https://ci.appveyor.com/api/projects/status/w4i5x8x9d4sbxhn2?svg=true)](https://ci.appveyor.com/project/yukinarit/pyserde)
[![Coverage Status](https://coveralls.io/repos/github/yukinarit/pyserde/badge.svg?branch=master)](https://coveralls.io/github/yukinarit/pyserde?branch=master)

Serialization library on top of [dataclasses](https://docs.python.org/3/library/dataclasses.html).

## Installation

```bash
$ pip install pyserde
```

## QuickStart

You can serialize/deserialize your class to/from various message formant (e.g. Json, MsgPack) quite easily!

```python
# main.py
# /usr/bin/env python

from dataclasses import dataclass
from serde import deserialize, serialize
from serde.json import from_json, to_json

# Mark the class serializable/deserializable.
@deserialize
@serialize
@dataclass
class Hoge:
    i: int
    s: str
    f: float
    b: bool

h = Hoge(i=10, s='hoge', f=100.0, b=True)

print(f"Into Json: {to_json(h)}")

s = '{"i": 10, "s": "hoge", "f": 100.0, "b": true}'

print(f"From Json: {from_json(Hoge, s)}")
```

```bash
$ python main.py
Into Json: {"i": 10, "s": "hoge", "f": 100.0, "b": true}
From Json: Hoge(i=10, s='hoge', f=100.0, b=True)
```

## Features

* Serializer
	* Json
	* MsgPack

## Documentation

https://yukinarit.github.io/pyserde/
