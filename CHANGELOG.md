## `0.8.3`  (2022-06-28)

* fix: Use numpy<1.23.0 for python 3.7 and 3.8 ([3045521](https://github.com/yukinarit/pyserde/commit/3045521))

## `0.8.2` (2022-06-18)

* chore: Replace stringcase with casfey ([1f8a17d](https://github.com/yukinarit/pyserde/commit/1f8a17d)), closes [#240](https://github.com/yukinarit/pyserde/issues/240)

This release had contributions from 1 person: [@gitpushdashf](https://github.com/gitpushdashf). Thank you so much! :tada: :joy:

## `0.8.1` (2022-06-14)

* feat: Don't wrap user exception in SerdeError ([161cffd](https://github.com/yukinarit/pyserde/commit/161cffd))

## `0.8.0` (2022-05-31)

Thanks to the contribution by [@kigawas](https://github.com/kigawas), pyserde can optionally use [orjson](supports://github.com/ijl/orjson) as JSON serializer!
```
pip install pyserde[orjson]
```
If orjson is installed in the system, pyserde automatically use orjson in [to_json](https://yukinarit.github.io/pyserde/api/serde/json.html#to_json)/[from_json](https://yukinarit.github.io/pyserde/api/serde/json.html#from_json).

**NOTE:** In order to align the JSON (de)serializer to orjson, a few parameters are passed in `json.dumps` internally. This would lead to a breaking change in some cases. If you need the same behaviour as in pyserde<0.8, please explicitely pass those parameters in `serde.json.to_json`. 🙇‍♂️
```python
to_json(obj, ensure_ascii=True, separators=(", ", ": "))
```

Other noteble chage is we have `@dataclass` decorator back in the all example and test code in the repository as shown below. It's because we found mypy isn't able to deduce the type correctly without `@dataclass` decorator.  If you are not mypy user, you can still declare a class with only `@serde` decorator. 👍 For more information, please read [the docs](https://yukinarit.github.io/pyserde/guide/features/decorators.html).

```python
@serde
@dataclass  # <-- Recommended to add @dataclass if you are mypy user.
class Foo:
    i: int
    s: str
    f: float
    b: bool
```

* build: Add "orjson" extras ([ea70ec1](https://github.com/yukinarit/pyserde/commit/ea70ec1))
* orjson support ([2744675](https://github.com/yukinarit/pyserde/commit/2744675))
* Update json.py ([2d67b65](https://github.com/yukinarit/pyserde/commit/2d67b65))
* feat: Support class declaration w/wo dataclass ([a35f909](https://github.com/yukinarit/pyserde/commit/a35f909))
* fix: Add dataclass decorator for all example code ([60567ab](https://github.com/yukinarit/pyserde/commit/60567ab))
* fix: Treat <type>|None as Optional ([5555452](https://github.com/yukinarit/pyserde/commit/5555452))
* Fix the default deserializer for custom class deserializer ([6c2245b](https://github.com/yukinarit/pyserde/commit/6c2245b))

This release had contributions from 1 person: [@kigawas](https://github.com/kigawas). Thank you so much! :tada: :joy:

## `0.7.3` (2022-05-10)

Thanks to the great contribution by [@kmsquire](https://github.com/kmsquire), pyserde supports some numpy types!

```python
@serde
class NPFoo:
    i: np.int32
    j: np.int64
    f: np.float32
    g: np.float64
    h: np.bool_
    u: np.ndarray
    v: npt.NDArray
    w: npt.NDArray[np.int32]
    x: npt.NDArray[np.int64]
    y: npt.NDArray[np.float32]
    z: npt.NDArray[np.float64]
```

* feat: Remove try-catch from is_numpy_array() (unnecessary) ([731876f](https://github.com/yukinarit/pyserde/commit/731876f))
* feat: Support Literal[...] type annotation ([e50c958](https://github.com/yukinarit/pyserde/commit/e50c958))
* feat: Support numpy types ([78eb22e](https://github.com/yukinarit/pyserde/commit/78eb22e))
* feat(compat): Only define np_get_origin() for python 3.8 or earlier ([02c5af2](https://github.com/yukinarit/pyserde/commit/02c5af2))
* feat(numpy): Support serialization of numpy.datetime64 ([5e521cf](https://github.com/yukinarit/pyserde/commit/5e521cf))
* Don't import tests module from pyserde package ([d664426](https://github.com/yukinarit/pyserde/commit/d664426))
* fix: Recognized numpy arrays on Python 3.7, 3.8 ([a0fa36f](https://github.com/yukinarit/pyserde/commit/a0fa36f))
* fix(numpy): Fix direct numpy array deserialization ([8f9f71c](https://github.com/yukinarit/pyserde/commit/8f9f71c))
* ci: Remove pypy-3.8 until a numpy wheel is released for it ([61b6130](https://github.com/yukinarit/pyserde/commit/61b6130))
* chore: Update black, fix test_union formatting ([4a708fd](https://github.com/yukinarit/pyserde/commit/4a708fd))
* chore: Update numpy version specification based on numpy compatibility with python ([1fa5e07](https://github.com/yukinarit/pyserde/commit/1fa5e07))

This release had contributions from 2 people: [@kmsquire](https://github.com/kmsquire) and [@chagui](https://github.com/chagui). Thank you so much! :tada: :joy:

## `0.7.2` (2022-04-11)

* Don't package tests and examples ([af829ae](https://github.com/yukinarit/pyserde/commit/af829ae)), closes [#214](https://github.com/yukinarit/pyserde/issues/214)
* ci: Use pypy-3.8 ([316b98e](https://github.com/yukinarit/pyserde/commit/316b98e))
* feat: Support PEP604 Union operator ([17419d2](https://github.com/yukinarit/pyserde/commit/17419d2))

This release had contributions from 1 person: [@gitpushdashf](https://github.com/gitpushdashf). Thank you so much! :tada: :joy:

## `0.7.1`  (2022-03-17)

* ci: Run tests on pull_request only ([015cb41](https://github.com/yukinarit/pyserde/commit/015cb41))
* feat: Support typing.Generic ([e9f2bdb](https://github.com/yukinarit/pyserde/commit/e9f2bdb))
* build: Drop python 3.6 and pypy ([279f1a4](https://github.com/yukinarit/pyserde/commit/279f1a4))
* docs: Fix typo in docs introduction ([03f24da](https://github.com/yukinarit/pyserde/commit/03f24da))

This release had contributions from 1 person: [@chagui](https://github.com/chagui). Thank you so much! :tada: :joy:

## `0.7.0` (2022-02-14)

* fix: Optional in custom class deserializer ([181b2f1](https://github.com/yukinarit/pyserde/commit/181b2f1))
* fix: raise SerdeError from serde's APIs ([76b0aee](https://github.com/yukinarit/pyserde/commit/76b0aee))
  * pyserde (de)serialize method used to raise various Exceptions such as KeyError. pyserde always raises SerdeError since v0.7.0
* core: using black formatting only if debug is enabled ([e596a84](https://github.com/yukinarit/pyserde/commit/e596a84))
* feat: Add _make_serialize and _make_deserialize ([a71c5d5](https://github.com/yukinarit/pyserde/commit/a71c5d5))
* feat: Implement Union tagging system ([c884dc4](https://github.com/yukinarit/pyserde/commit/c884dc4))
  * This will change the default tagging for dataclasses with Union from `Untagged` to `ExternalTagging`. **This may break the existing code**, so please be aware if you use dataclasses with Union. For more information, check [the documentation](docs/features/union.md)
* build: Update mypy to workaround typed_ast error ([0ea33a7](https://github.com/yukinarit/pyserde/commit/0ea33a7))

This release had contributions from 1 person: [@tardyp](https://github.com/tardyp). Thank you so much! :tada: :joy:

## `0.6.0` (2021-12-20)

* feat: Add @serde decorator ([523dc9c](https://github.com/yukinarit/pyserde/commit/523dc9c))
* feat: Add serde field function ([488bf00](https://github.com/yukinarit/pyserde/commit/488bf00))
* feat: Add serde_skip_default field attribute ([0f0b212](https://github.com/yukinarit/pyserde/commit/0f0b212))
* feat: Automatically put dataclass decorator ([2f0cf01](https://github.com/yukinarit/pyserde/commit/2f0cf01))

With `serde` decorator and `field` function, you can declare pyserde class more easily.

```python
from serde import serde, field

@serde
class Foo:
    a : List[str] = field(default_factory=list, skip_if_false=True)
```

The declaration until v0.5.3 still works.

```python
from dataclasses import dataclass
from serde import serialize, deserialize

@deserialize
@serialize
@dataclass
class Foo:
    a : List[str] = field(default_factory=list, metadata={'serde_skip_if_false': True})
```

## `0.5.3` (2021-11-24)

* feat: Add more dataclass Field's attrs to Field ([7b57c53](https://github.com/yukinarit/pyserde/commit/7b57c53))
* feat: Support python 3.10 ([2f0c557](https://github.com/yukinarit/pyserde/commit/2f0c557))
* refactor: Delete unused imports ([629d040](https://github.com/yukinarit/pyserde/commit/629d040))
* refactor: Remove type references from SerdeScope ([bdd8784](https://github.com/yukinarit/pyserde/commit/bdd8784))
* refactor: Speficy correct type bound for serde.core.fields ([c3b555c](https://github.com/yukinarit/pyserde/commit/c3b555c))
* fix: Add types in typing module to scope ([e12e802](https://github.com/yukinarit/pyserde/commit/e12e802))
* fix: Never use default value for from_tuple ([3ce4f6b](https://github.com/yukinarit/pyserde/commit/3ce4f6b))
* fix: Use default value only if key isn't present ([3fa4ab6](https://github.com/yukinarit/pyserde/commit/3fa4ab6))
* Fix typo in README ([5f957d0](https://github.com/yukinarit/pyserde/commit/5f957d0))

This release had contributions from 2 people: [@rnestler](https://github.com/rnestler), [@mauvealerts](https://github.com/mauvealerts). Thank you so much! :tada: :joy:

## `0.5.2` (2021-10-21)

* feat: (de)serialize non dataclass types correctly ([0ffb9ea](https://github.com/yukinarit/pyserde/commit/0ffb9ea))
* refactor: Fix minor type error ([bef0c4f](https://github.com/yukinarit/pyserde/commit/bef0c4f))
* refactor: Remove unused imports ([cc16d58](https://github.com/yukinarit/pyserde/commit/cc16d58))
* refactor: Use backports-datetime-fromisoformat for python 3.6 ([014296f](https://github.com/yukinarit/pyserde/commit/014296f))
* build: Remove unused dependency for examples ([3a5ca01](https://github.com/yukinarit/pyserde/commit/3a5ca01))

## `0.5.1` (2021-10-10)

* feat: deserialize to the type more correctly ([a4c155c](https://github.com/yukinarit/pyserde/commit/a4c155c))
* refactor: import minimum names ([f242a93](https://github.com/yukinarit/pyserde/commit/f242a93))

## `0.5.0` (2021-09-30)

* New documentation is available!
    * [Guide](https://yukinarit.github.io/pyserde/guide/)
    * [API Docs](https://yukinarit.github.io/pyserde/api/serde.html)
* feat: Implement flatten ([a7bb6f0](https://github.com/yukinarit/pyserde/commit/a7bb6f0))

```python
@deserialize
@serialize
@dataclass
class Bar:
    c: float
    d: bool

@deserialize
@serialize
@dataclass
class Foo:
    a: int
    b: str
    bar: Bar = field(metadata={'serde_flatten': True})
```

* feat: Print Tips in serde.inspect ([62c74f3](https://github.com/yukinarit/pyserde/commit/62c74f3))
* fix: "Cannot instantiate type" type error ([6b3afbd](https://github.com/yukinarit/pyserde/commit/6b3afbd))
* ci: Use actions-comment-pull-request@1.0.2 ([45a999c](https://github.com/yukinarit/pyserde/commit/45a999c))
* build: Parallel test execution ([#148](https://github.com/yukinarit/pyserde/pull/148))
* build: Migrate to poetry ([#144](https://github.com/yukinarit/pyserde/pull/144))

This release had contributions from 1 person: [@alexmisk](https://github.com/alexmisk). Thank you so much! :tada: :joy:

## `0.4.0` (2021-06-17)

* feat: add support for lazy annotations PEP563 (#112) ([f7f6996](https://github.com/yukinarit/pyserde/commit/f7f6996)), closes [#112](https://github.com/yukinarit/pyserde/issues/112)

```python
from __future__ import annotations
from dataclasses import dataclass
from serde import deserialize, serialize

@deserialize
@serialize
@dataclass
class Foo:
    i: int
    s: str
    f: float
    b: bool

    def foo(self, cls: Foo):  # You can use "Foo" type before it's defined.
        print('foo')
```

* feat: Implement custom class (de)serializer ([3484d46](https://github.com/yukinarit/pyserde/commit/3484d46))
* feat: Implement custom field (de)serializer ([14b791c](https://github.com/yukinarit/pyserde/commit/14b791c))

```python
def serializer(cls, o):
    ...

def deserializer(cls, o):
    ...

@deserialize(deserializer=deserializer)
@serialize(serializer=serializer)
@dataclass
class Foo:
    i: int
    # Class serializer/deserializer is used as default.
    dt1: datetime
    # Override by field serializer/deserializer.
    dt2: datetime = field(
        metadata={
            'serde_serializer': lambda x: x.strftime('%y.%m.%d'),
            'serde_deserializer': lambda x: datetime.strptime(x, '%y.%m.%d'),
        }
    )
```

* feat: Improve error description for union type ([8abb549](https://github.com/yukinarit/pyserde/commit/8abb549))
* feat: Improve serde.inspect ([8b8635a](https://github.com/yukinarit/pyserde/commit/8b8635a))
* feat: Support typing.any ([988a621](https://github.com/yukinarit/pyserde/commit/988a621))
* feat: Support typing.NewType for primitives ([731ed79](https://github.com/yukinarit/pyserde/commit/731ed79))
* refactor: Add lvalue renderer for serialization ([665dc77](https://github.com/yukinarit/pyserde/commit/665dc77))
* refactor: Remove arg template filter from se.py ([0377655](https://github.com/yukinarit/pyserde/commit/0377655))
* refactor: Remove self class from scope ([da81f1f](https://github.com/yukinarit/pyserde/commit/da81f1f))
* refactor: Rename custom (de)serializer attributes ([03b2274](https://github.com/yukinarit/pyserde/commit/03b2274))
* ci: Add python 3.10-dev to CI pipeline ([1f33e59](https://github.com/yukinarit/pyserde/commit/1f33e59))
* ci: Don't cache pip to workaround pip error ([c912429](https://github.com/yukinarit/pyserde/commit/c912429))
* build: add pre-commit to test requirements ([a88ea40](https://github.com/yukinarit/pyserde/commit/a88ea40))
* fix: correctly render single element tuples ([a8a6456](https://github.com/yukinarit/pyserde/commit/a8a6456))
* fix: pass convert_sets argument to union functions ([ab40cc9](https://github.com/yukinarit/pyserde/commit/ab40cc9))
* fix: support unions with nested unions in containers (#113) ([c26e828](https://github.com/yukinarit/pyserde/commit/c26e828)), closes [#113](https://github.com/yukinarit/pyserde/issues/113)

This release had contributions from 1 person: [@ydylla](https://github.com/ydylla). Thank you so much! :tada: :joy:

## `0.3.2` (2021-05-07)

* feat: Improve error description for union type ([8abb549](https://github.com/yukinarit/pyserde/commit/8abb549))
* feat: Improve serde.inspect ([8b8635a](https://github.com/yukinarit/pyserde/commit/8b8635a))
* feat: Support typing.any ([988a621](https://github.com/yukinarit/pyserde/commit/988a621))
* feat: Support typing.NewType for primitives ([731ed79](https://github.com/yukinarit/pyserde/commit/731ed79))
* build: add pre-commit to test requirements ([a88ea40](https://github.com/yukinarit/pyserde/commit/a88ea40))
* fix: correctly render single element tuples ([a8a6456](https://github.com/yukinarit/pyserde/commit/a8a6456))
* fix: pass convert_sets argument to union functions ([ab40cc9](https://github.com/yukinarit/pyserde/commit/ab40cc9))
* fix: support unions with nested unions in containers (#113) ([c26e828](https://github.com/yukinarit/pyserde/commit/c26e828)), closes [#113](https://github.com/yukinarit/pyserde/issues/113)
* ci: Don't cache pip to workaround pip error ([c912429](https://github.com/yukinarit/pyserde/commit/c912429))
* refactor: Remove self class from scope ([da81f1f](https://github.com/yukinarit/pyserde/commit/da81f1f))

This release had contributions from 1 person: [@ydylla](https://github.com/ydylla). Thank you so much! :tada: :joy:

## `0.3.1` (2021-03-21)

* fix: Add type annotation to serde decorators ([f885a27](https://github.com/yukinarit/pyserde/commit/f885a27))

You can get the code completion from the class with `serialize` and `deserialize` decorators. I would recommend everyone to upgrade to v0.3.1.

## `0.3.0` (2021-03-20)

* feat: Support PEP585 type hint annotation ([81d3f4f](https://github.com/yukinarit/pyserde/commit/81d3f4f))
    ```python
    @deserialize
    @serialize
    @dataclass
    class Foo:
        l: list[str]
        t: tuple[str, bool]
        d: dict[str, list[int]]
    ```
* feat: add support for typing.Set & set ([20a4cdc](https://github.com/yukinarit/pyserde/commit/20a4cdc))
* feat: add more types & use code generation ([d352d2d](https://github.com/yukinarit/pyserde/commit/d352d2d))
    * IPv4Address, IPv6Address, IPv4Network, IPv6Network, IPv4Interface, IPv6Interface
    * PosixPath, WindowsPath, PurePath, PurePosixPath, PureWindowsPath
    * UUID
* feat: add convert_sets option required for to_json & to_msgpack ([f954586](https://github.com/yukinarit/pyserde/commit/f954586))
* feat: add union support for complex types ([434edf6](https://github.com/yukinarit/pyserde/commit/434edf6))
    ```python
    @deserialize
    @serialize
    @dataclass
    class Foo:
        v: Union[int, str]
        c: Union[Dict[str, int], List[int]]
    ```
* fix: Ellipsis overwriting configured default for reuse_instances ([b0366e5](https://github.com/yukinarit/pyserde/commit/b0366e5))
* fix: forward reuse_instances & fix call order for optionals ([c56128c](https://github.com/yukinarit/pyserde/commit/c56128c))
* fix: compatibility with python 3.6 ([7ae87b4](https://github.com/yukinarit/pyserde/commit/7ae87b4))
* fix: this pytest option does not exist #58 ([c5938da](https://github.com/yukinarit/pyserde/commit/c5938da)), closes [#58](https://github.com/yukinarit/pyserde/issues/58)
* fix: scope should not be shared between classes ([889ada1](https://github.com/yukinarit/pyserde/commit/889ada1))
* fix: use iter_unions to recursively collect all unions of dataclass ([577aeb9](https://github.com/yukinarit/pyserde/commit/577aeb9))
* build: Add PEP561 py.typed marker file ([c0f46b9](https://github.com/yukinarit/pyserde/commit/c0f46b9))
* build: Don't install dataclasses for python>3.6 ([f47caa9](https://github.com/yukinarit/pyserde/commit/f47caa9))
* build: setup pre-commit as formatting tool ([2876de4](https://github.com/yukinarit/pyserde/commit/2876de4))
* ci: add code style check ([c52f7e9](https://github.com/yukinarit/pyserde/commit/c52f7e9))

This release had contributions from 2 people: [@ydylla](https://github.com/ydylla), [@alexmisk](https://github.com/alexmisk). Thank you so much! :tada: :joy:

## `0.2.2` (2021-01-19)

* Support inference of types on deserialization ([8c4efb2](https://github.com/yukinarit/pyserde/commit/8c4efb2))
* Fix pytest error ([09ee66a](https://github.com/yukinarit/pyserde/commit/09ee66a))

This release had contibutions from 1 person: [@adsharma](https://github.com/adsharma). Thank you so much! :tada: :joy:

## `0.2.1` (2020-11-29)

* feat: Allow enum compatible value for enum field ([14006ee](https://github.com/yukinarit/pyserde/commit/14006ee))
* fix: Support optional extended types ([d0418fc](https://github.com/yukinarit/pyserde/commit/d0418fc))
* Added example of a field with default_factory property ([6740aaa](https://github.com/yukinarit/pyserde/commit/6740aaa))
* Add Codecov.io integration ([#56](https://github.com/yukinarit/pyserde/pull/56))
* CI improvements ([#68](https://github.com/yukinarit/pyserde/pull/68))
    * Explicitly pass Python version to pipenv
    * Rename testing step for better readability
    * Change Python 3.9-dev to 3.9 in test matrix

This release had contributions from 2 people: [@alexmisk](https://github.com/alexmisk), [@pranavvp10](https://github.com/pranavvp10). Thank you so much! :turkey: :joy:

## `0.2.0` (2020-10-31)

Please note this release has a breaking change, where `pip install pyserde` no longer installs `msgpack`, `pyyaml` and `toml`. If you want the same behavior as in 0.1.5, use `pip install pyserde[all]`.

* fix: Don't initialize scope with global scole ([dc58f2a](https://github.com/yukinarit/pyserde/commit/dc58f2a))
* fix: Rework "default" support for deserialize ([bd64fa3](https://github.com/yukinarit/pyserde/commit/bd64fa3))
* Migrate from Travis to Github Action ([#45](https://github.com/yukinarit/pyserde/pull/45))
* Make data format dependencies optional ([4a130ab](https://github.com/yukinarit/pyserde/commit/4a130ab))

This release had contributions from 2 people: [@alexmisk](https://github.com/alexmisk), [@andreymal](https://github.com/andreymal). Thank you so much! :tada: :joy:

## `0.1.5` (2020-10-05)

* fix: Type error ([2a271ac](https://github.com/yukinarit/pyserde/commit/2a271acf32bb7b37546d0037ac5b62f39cdc5bb3))
* feat: Now supports Optional of Enum/IntEnum class ([e3618e5](https://github.com/yukinarit/pyserde/commit/e3618e5daea30cb787e80a0f3df23438c8bffcef))

## `0.1.4` (2020-09-25)

* feat: Enum support ([6dca279](https://github.com/yukinarit/pyserde/commit/6dca2792c32ceadbfdbd6e8aa50c0ac511661e7d))

## `0.1.3` (2020-09-12)

* fix: Fix "has no attribute 'mangle'" error ([c71cb3b](https://github.com/yukinarit/pyserde/commit/c71cb3b5aaad16d008d0220a72c119ee0fbddc1a))

## `0.1.2` (2020-08-01)

* feat: Add support for pathlib.Path fields ([28c8c1a](https://github.com/yukinarit/pyserde/commit/28c8c1a))

## `0.1.1` (2020-04-23)

* fix: astuple incorrectly deserialize dict ([dfd69e8](https://github.com/yukinarit/pyserde/commit/dfd69e8))
