# Benchmark

* macOS 10.14 Mojave
* Intel 2.3GHz 8-core Intel Core i9
* DDR4 32GB RAM

Serialize and deserialize a [struct](https://github.com/yukinarit/pyserde/blob/master/bench/dataclasses_class.py#L7-L12) into and from json 10,000 times.

| Serialize | Deserialize |
|-----------|-------------|
| <img src="https://raw.githubusercontent.com/yukinarit/pyserde/master/bench/charts/se-small.png"> | <img src="https://raw.githubusercontent.com/yukinarit/pyserde/master/bench/charts/de-small.png"> |

Serialize the struct into tuple and dictionary.

| to_tuple | to_dict |
|-----------|-------------|
| <img src="https://raw.githubusercontent.com/yukinarit/pyserde/master/bench/charts/astuple-small.png"> | <img src="https://raw.githubusercontent.com/yukinarit/pyserde/master/bench/charts/asdict-small.png"> |

* `raw`: Serialize and deserialize manually. Fastest in theory.
* `dataclass`: Serialize using dataclass's asdict.
* `pyserde`: This library.
* [`dacite`](https://github.com/konradhalas/dacite): Simple creation of data classes from dictionaries.
* [`mashumaro`](https://github.com/Fatal1ty/mashumaro): Fast and well tested serialization framework on top of dataclasses.
* [`marshallow`](https://github.com/marshmallow-code/marshmallow): A lightweight library for converting complex objects to and from simple datatypes.
* [`attrs`](https://github.com/python-attrs/attrs): Python Classes Without Boilerplate.
* [`cattrs`](https://github.com/Tinche/cattrs): Complex custom class converters for attrs.

To run benchmark in your environment:

```sh
git clone git@github.com:yukinarit/pyserde.git
cd pyserde/bench
poetry install
poetry run python bench.py --full
```

You can check [the benchmarking code](https://github.com/yukinarit/pyserde/blob/master/bench/bench.py) for more information.
