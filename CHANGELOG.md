## 0.3.1 (2021-03-21)

* fix: Add type annotation to serde decorators ([f885a27](https://github.com/yukinarit/pyserde/commit/f885a27))

You can get the code completion from the class with `serialize` and `deserialize` decorators. I would recommend everyone to upgrade to v0.3.1.

## 0.3.0 (2021-03-20)

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

This release had contibutions from 2 people: [@ydylla](https://github.com/ydylla), [@alexmisk](https://github.com/alexmisk). Thank you so much! :tada: :joy:

## 0.2.2 (2021-01-19)

* Support inference of types on deserialization ([8c4efb2](https://github.com/yukinarit/pyserde/commit/8c4efb2))
* Fix pytest error ([09ee66a](https://github.com/yukinarit/pyserde/commit/09ee66a))

This release had contibutions from 1 person: [@adsharma](https://github.com/adsharma). Thank you so much! :tada: :joy:

## 0.2.1 (2020-11-29)

* feat: Allow enum compatible value for enum field ([14006ee](https://github.com/yukinarit/pyserde/commit/14006ee))
* fix: Support optional extended types ([d0418fc](https://github.com/yukinarit/pyserde/commit/d0418fc))
* Added example of a field with default_factory property ([6740aaa](https://github.com/yukinarit/pyserde/commit/6740aaa))
* Add Codecov.io integration ([#56](https://github.com/yukinarit/pyserde/pull/56))
* CI improvements ([#68](https://github.com/yukinarit/pyserde/pull/68))
    * Explicitly pass Python version to pipenv
    * Rename testing step for better readability
    * Change Python 3.9-dev to 3.9 in test matrix

This release had contibutions from 2 people: [@alexmisk](https://github.com/alexmisk), [@pranavvp10](https://github.com/pranavvp10). Thank you so much! :turkey: :joy:

## 0.2.0 (2020-10-31)

Please note this release has a breaking change, where `pip install pyserde` no longer installs `msgpack`, `pyyaml` and `toml`. If you want the same behavior as in 0.1.5, use `pip install pyserde[all]`.

* fix: Don't initialize scope with global scole ([dc58f2a](https://github.com/yukinarit/pyserde/commit/dc58f2a))
* fix: Rework "default" support for deserialize ([bd64fa3](https://github.com/yukinarit/pyserde/commit/bd64fa3))
* Migrate from Travis to Github Action ([#45](https://github.com/yukinarit/pyserde/pull/45))
* Make data format dependencies optional ([4a130ab](https://github.com/yukinarit/pyserde/commit/4a130ab))

This release had contibutions from 2 people: [@alexmisk](https://github.com/alexmisk), [@andreymal](https://github.com/andreymal). Thank you so much! :tada: :joy:

## 0.1.5 (2020-10-05)

* fix: Type error ([2a271ac](https://github.com/yukinarit/pyserde/commit/2a271acf32bb7b37546d0037ac5b62f39cdc5bb3))
* feat: Now supports Optional of Enum/IntEnum class ([e3618e5](https://github.com/yukinarit/pyserde/commit/e3618e5daea30cb787e80a0f3df23438c8bffcef))

## 0.1.4 (2020-09-25)

* feat: Enum support ([6dca279](https://github.com/yukinarit/pyserde/commit/6dca2792c32ceadbfdbd6e8aa50c0ac511661e7d))

## 0.1.3 (2020-09-12)

* fix: Fix "has no attribute 'mangle'" error ([c71cb3b](https://github.com/yukinarit/pyserde/commit/c71cb3b5aaad16d008d0220a72c119ee0fbddc1a))

## 0.1.2 (2020-08-01)

* feat: Add support for pathlib.Path fields ([28c8c1a](https://github.com/yukinarit/pyserde/commit/28c8c1a))

## 0.1.1 (2020-04-23)

* fix: astuple incorrectly deserialize dict ([dfd69e8](https://github.com/yukinarit/pyserde/commit/dfd69e8))
