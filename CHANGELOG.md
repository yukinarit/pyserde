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
