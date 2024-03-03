<h1 align="center"><code>pyserde</code></h1>
<p align="center">Yet another serialization library on top of <a href="https://docs.python.org/3/library/dataclasses.html">dataclasses</a>, inspired by <a href="https://github.com/serde-rs/serde">serde-rs</a>.</p>
<p align="center">
  <a href="https://pypi.org/project/pyserde/">
    <img alt="pypi" src="https://img.shields.io/pypi/v/pyserde.svg">
  </a>
  <a href="https://pypi.org/project/pyserde/">
    <img alt="pypi" src="https://img.shields.io/pypi/pyversions/pyserde.svg">
  </a>
  <a href="https://github.com/yukinarit/pyserde/actions/workflows/test.yml">
    <img alt="GithubActions" src="https://github.com/yukinarit/pyserde/actions/workflows/test.yml/badge.svg">
  </a>
  <a href="https://codecov.io/gh/yukinarit/pyserde">
    <img alt="CodeCov" src="https://codecov.io/gh/yukinarit/pyserde/branch/main/graph/badge.svg">
  </a>
</p>
<p align="center">
  <a href="https://yukinarit.github.io/pyserde/guide/en">Guide</a> | <a href="https://yukinarit.github.io/pyserde/api/serde.html">API Docs</a> | <a href="https://github.com/yukinarit/pyserde/tree/main/examples">Examples</a>
</p>

## Overview

Declare a class with pyserde's `@serde` decorator.

```python
@serde
@dataclass
class Foo:
    i: int
    s: str
    f: float
    b: bool
```

You can serialize `Foo` object into JSON.

```python
>>> to_json(Foo(i=10, s='foo', f=100.0, b=True))
'{"i":10,"s":"foo","f":100.0,"b":true}'
```

You can deserialize JSON into `Foo` object.
```python
>>> from_json(Foo, '{"i": 10, "s": "foo", "f": 100.0, "b": true}')
Foo(i=10, s='foo', f=100.0, b=True)
```

## Features

- Supported data formats
    - dict
    - tuple
    - JSON
	- Yaml
	- Toml
	- MsgPack
    - Pickle
- Supported types
    - Primitives (`int`, `float`, `str`, `bool`)
    - Containers
        - `List`, `Set`, `Tuple`, `Dict`
        - [`FrozenSet`](https://docs.python.org/3/library/stdtypes.html#frozenset), [`DefaultDict`](https://docs.python.org/3/library/collections.html#collections.defaultdict)
    - [`typing.Optional`](https://docs.python.org/3/library/typing.html#typing.Optional)
    - [`typing.Union`](https://docs.python.org/3/library/typing.html#typing.Union)
    - User defined class with [`@dataclass`](https://docs.python.org/3/library/dataclasses.html)
    - [`typing.NewType`](https://docs.python.org/3/library/typing.html#newtype) for primitive types
    - [`typing.Any`](https://docs.python.org/3/library/typing.html#the-any-type)
    - [`typing.Literal`](https://docs.python.org/3/library/typing.html#typing.Literal)
    - [`typing.Generic`](https://docs.python.org/3/library/typing.html#user-defined-generic-types)
    - [`typing.ClassVar`](https://docs.python.org/3/library/typing.html#typing.ClassVar)
    - [`dataclasses.InitVar`](https://docs.python.org/3/library/dataclasses.html#init-only-variables)
    - [`Enum`](https://docs.python.org/3/library/enum.html#enum.Enum) and [`IntEnum`](https://docs.python.org/3/library/enum.html#enum.IntEnum)
    - Standard library
        - [`pathlib.Path`](https://docs.python.org/3/library/pathlib.html)
        - [`decimal.Decimal`](https://docs.python.org/3/library/decimal.html)
        - [`uuid.UUID`](https://docs.python.org/3/library/uuid.html)
        - [`datetime.date`](https://docs.python.org/3/library/datetime.html#date-objects), [`datetime.time`](https://docs.python.org/3/library/datetime.html#time-objects), [`datetime.datetime`](https://docs.python.org/3/library/datetime.html#datetime-objects)
        - [`ipaddress`](https://docs.python.org/3/library/ipaddress.html)
    - PyPI library
        - [`numpy`](https://github.com/numpy/numpy) types
- [Class Attributes](https://github.com/yukinarit/pyserde/blob/main/docs/en/class-attributes.md)
- [Field Attributes](https://github.com/yukinarit/pyserde/blob/main/docs/en/field-attributes.md)
- [Decorators](https://github.com/yukinarit/pyserde/blob/main/docs/en/decorators.md)
- [Type Check](https://github.com/yukinarit/pyserde/blob/main/docs/en/type-check.md)
- [Union Representation](https://github.com/yukinarit/pyserde/blob/main/docs/en/union.md)
- [Forward reference](https://github.com/yukinarit/pyserde/blob/main/docs/en/decorators.md#how-can-i-use-forward-references)
- [PEP563 Postponed Evaluation of Annotations](https://github.com/yukinarit/pyserde/blob/main/docs/en/decorators.md#pep563-postponed-evaluation-of-annotations)
- [PEP585 Type Hinting Generics In Standard Collections](https://github.com/yukinarit/pyserde/blob/main/docs/en/getting-started.md#pep585-and-pep604)
- [PEP604 Allow writing union types as X | Y](https://github.com/yukinarit/pyserde/blob/main/docs/en/getting-started.md#pep585-and-pep604)
- [PEP681 Data Class Transform](https://github.com/yukinarit/pyserde/blob/main/docs/en/decorators.md#serde)
- [Case Conversion](https://github.com/yukinarit/pyserde/blob/main/docs/en/class-attributes.md#rename_all)
- [Rename](https://github.com/yukinarit/pyserde/blob/main/docs/en/field-attributes.md#rename)
- [Alias](https://github.com/yukinarit/pyserde/blob/main/docs/en/field-attributes.md#alias)
- Skip (de)serialization ([skip](https://github.com/yukinarit/pyserde/blob/main/docs/en/field-attributes.md#skip), [skip_if](https://github.com/yukinarit/pyserde/blob/main/docs/en/field-attributes.md#skip_if), [skip_if_false](https://github.com/yukinarit/pyserde/blob/main/docs/en/field-attributes.md#skip_if_false), [skip_if_default](https://github.com/yukinarit/pyserde/blob/main/docs/en/field-attributes.md#skip_if_default))
- [Custom field (de)serializer](https://github.com/yukinarit/pyserde/blob/main/docs/en/field-attributes.md#serializerdeserializer)
- [Custom class (de)serializer](https://github.com/yukinarit/pyserde/blob/main/docs/en/class-attributes.md#class_serializer--class_deserializer)
- [Custom global (de)serializer](https://github.com/yukinarit/pyserde/blob/main/docs/en/extension.md#custom-global-deserializer)
- [Flatten](https://github.com/yukinarit/pyserde/blob/main/docs/en/field-attributes.md#flatten)

## Extensions

* [pyserde-timedelta](https://github.com/yukinarit/pyserde-timedelta): (de)serializing datetime.timedelta in ISO 8601 duration format.

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/yukinarit"><img src="https://avatars.githubusercontent.com/u/2347533?v=4?s=60" width="60px;" alt="yukinarit"/><br /><sub><b>yukinarit</b></sub></a><br /><a href="https://github.com/yukinarit/pyserde/commits?author=yukinarit" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/alexmisk"><img src="https://avatars.githubusercontent.com/u/4103218?v=4?s=60" width="60px;" alt="Alexander Miskaryan"/><br /><sub><b>Alexander Miskaryan</b></sub></a><br /><a href="https://github.com/yukinarit/pyserde/commits?author=alexmisk" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/ydylla"><img src="https://avatars.githubusercontent.com/u/17772145?v=4?s=60" width="60px;" alt="ydylla"/><br /><sub><b>ydylla</b></sub></a><br /><a href="https://github.com/yukinarit/pyserde/commits?author=ydylla" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/kmsquire"><img src="https://avatars.githubusercontent.com/u/223250?v=4?s=60" width="60px;" alt="Kevin Squire"/><br /><sub><b>Kevin Squire</b></sub></a><br /><a href="https://github.com/yukinarit/pyserde/commits?author=kmsquire" title="Code">💻</a> <a href="https://github.com/yukinarit/pyserde/commits?author=kmsquire" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://yushiomote.org/"><img src="https://avatars.githubusercontent.com/u/3733915?v=4?s=60" width="60px;" alt="Yushi OMOTE"/><br /><sub><b>Yushi OMOTE</b></sub></a><br /><a href="https://github.com/yukinarit/pyserde/commits?author=YushiOMOTE" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://kngwyu.github.io/"><img src="https://avatars.githubusercontent.com/u/16046705?v=4?s=60" width="60px;" alt="Yuji Kanagawa"/><br /><sub><b>Yuji Kanagawa</b></sub></a><br /><a href="https://github.com/yukinarit/pyserde/commits?author=kngwyu" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://kigawas.me/"><img src="https://avatars.githubusercontent.com/u/4182346?v=4?s=60" width="60px;" alt="Weiliang Li"/><br /><sub><b>Weiliang Li</b></sub></a><br /><a href="https://github.com/yukinarit/pyserde/commits?author=kigawas" title="Code">💻</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/mauvealerts"><img src="https://avatars.githubusercontent.com/u/51870303?v=4?s=60" width="60px;" alt="Mauve"/><br /><sub><b>Mauve</b></sub></a><br /><a href="https://github.com/yukinarit/pyserde/commits?author=mauvealerts" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/adsharma"><img src="https://avatars.githubusercontent.com/u/658691?v=4?s=60" width="60px;" alt="adsharma"/><br /><sub><b>adsharma</b></sub></a><br /><a href="https://github.com/yukinarit/pyserde/commits?author=adsharma" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/chagui"><img src="https://avatars.githubusercontent.com/u/1234128?v=4?s=60" width="60px;" alt="Guilhem C."/><br /><sub><b>Guilhem C.</b></sub></a><br /><a href="https://github.com/yukinarit/pyserde/commits?author=chagui" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/tardyp"><img src="https://avatars.githubusercontent.com/u/109859?v=4?s=60" width="60px;" alt="Pierre Tardy"/><br /><sub><b>Pierre Tardy</b></sub></a><br /><a href="https://github.com/yukinarit/pyserde/commits?author=tardyp" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://blog.rnstlr.ch/"><img src="https://avatars.githubusercontent.com/u/1435346?v=4?s=60" width="60px;" alt="Raphael Nestler"/><br /><sub><b>Raphael Nestler</b></sub></a><br /><a href="https://github.com/yukinarit/pyserde/commits?author=rnestler" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://pranavvp10.github.io/"><img src="https://avatars.githubusercontent.com/u/52486224?v=4?s=60" width="60px;" alt="Pranav V P"/><br /><sub><b>Pranav V P</b></sub></a><br /><a href="https://github.com/yukinarit/pyserde/commits?author=pranavvp10" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://andreymal.org/"><img src="https://avatars.githubusercontent.com/u/3236464?v=4?s=60" width="60px;" alt="andreymal"/><br /><sub><b>andreymal</b></sub></a><br /><a href="https://github.com/yukinarit/pyserde/commits?author=andreymal" title="Code">💻</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/jfuechsl"><img src="https://avatars.githubusercontent.com/u/1097068?v=4?s=60" width="60px;" alt="Johann Fuechsl"/><br /><sub><b>Johann Fuechsl</b></sub></a><br /><a href="https://github.com/yukinarit/pyserde/commits?author=jfuechsl" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/DoeringChristian"><img src="https://avatars.githubusercontent.com/u/23581448?v=4?s=60" width="60px;" alt="DoeringChristian"/><br /><sub><b>DoeringChristian</b></sub></a><br /><a href="https://github.com/yukinarit/pyserde/commits?author=DoeringChristian" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://stuart.axelbrooke.com/"><img src="https://avatars.githubusercontent.com/u/2815794?v=4?s=60" width="60px;" alt="Stuart Axelbrooke"/><br /><sub><b>Stuart Axelbrooke</b></sub></a><br /><a href="https://github.com/yukinarit/pyserde/commits?author=soaxelbrooke" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://kobzol.github.io/"><img src="https://avatars.githubusercontent.com/u/4539057?v=4?s=60" width="60px;" alt="Jakub Beránek"/><br /><sub><b>Jakub Beránek</b></sub></a><br /><a href="https://github.com/yukinarit/pyserde/commits?author=Kobzol" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Fredrik-Reinholdsen"><img src="https://avatars.githubusercontent.com/u/11893023?v=4?s=60" width="60px;" alt="Fredrik Reinholdsen"/><br /><sub><b>Fredrik Reinholdsen</b></sub></a><br /><a href="https://github.com/yukinarit/pyserde/commits?author=Fredrik-Reinholdsen" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.patreon.com/nicoddemus"><img src="https://avatars.githubusercontent.com/u/1085180?v=4?s=60" width="60px;" alt="Bruno Oliveira"/><br /><sub><b>Bruno Oliveira</b></sub></a><br /><a href="https://github.com/yukinarit/pyserde/commits?author=nicoddemus" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://kylekosic.dev/"><img src="https://avatars.githubusercontent.com/u/23020003?v=4?s=60" width="60px;" alt="Kyle Kosic"/><br /><sub><b>Kyle Kosic</b></sub></a><br /><a href="https://github.com/yukinarit/pyserde/commits?author=kykosic" title="Code">💻</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/gpetrovic-meltin"><img src="https://avatars.githubusercontent.com/u/72957645?v=4?s=60" width="60px;" alt="Gajo Petrovic"/><br /><sub><b>Gajo Petrovic</b></sub></a><br /><a href="https://github.com/yukinarit/pyserde/commits?author=gpetrovic-meltin" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/m472"><img src="https://avatars.githubusercontent.com/u/6155240?v=4?s=60" width="60px;" alt="m472"/><br /><sub><b>m472</b></sub></a><br /><a href="https://github.com/yukinarit/pyserde/commits?author=m472" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/acolley-gel"><img src="https://avatars.githubusercontent.com/u/90254318?v=4?s=60" width="60px;" alt="acolley-gel"/><br /><sub><b>acolley-gel</b></sub></a><br /><a href="https://github.com/yukinarit/pyserde/commits?author=acolley-gel" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/maallaire"><img src="https://avatars.githubusercontent.com/u/38792535?v=4?s=60" width="60px;" alt="Marc-André Allaire"/><br /><sub><b>Marc-André Allaire</b></sub></a><br /><a href="https://github.com/yukinarit/pyserde/commits?author=maallaire" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/gschaffner"><img src="https://avatars.githubusercontent.com/u/11418203?v=4?s=60" width="60px;" alt="Ganden Schaffner"/><br /><sub><b>Ganden Schaffner</b></sub></a><br /><a href="https://github.com/yukinarit/pyserde/commits?author=gschaffner" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/davetapley"><img src="https://avatars.githubusercontent.com/u/48232?v=4?s=60" width="60px;" alt="Dave Tapley"/><br /><sub><b>Dave Tapley</b></sub></a><br /><a href="https://github.com/yukinarit/pyserde/commits?author=davetapley" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/uyha"><img src="https://avatars.githubusercontent.com/u/8091245?v=4?s=60" width="60px;" alt="Beartama"/><br /><sub><b>Beartama</b></sub></a><br /><a href="https://github.com/yukinarit/pyserde/commits?author=uyha" title="Code">💻</a></td>
    </tr>
  </tbody>
  <tfoot>
    <tr>
      <td align="center" size="13px" colspan="7">
        <img src="https://raw.githubusercontent.com/all-contributors/all-contributors-cli/1b8533af435da9854653492b1327a23a4dbd0a10/assets/logo-small.svg">
          <a href="https://all-contributors.js.org/docs/en/bot/usage">Add your contributions</a>
        </img>
      </td>
    </tr>
  </tfoot>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!

## LICENSE

This project is licensed under the [MIT license](https://github.com/yukinarit/pyserde/blob/main/LICENSE).
