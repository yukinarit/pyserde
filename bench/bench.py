import sys
import functools
import json
import timeit
from typing import Dict, List, Type, Tuple

import dacite
import dataclasses_json
import dataclasses_jsonschema
import ix
import mashumaro
import pavlova
from dataclasses import asdict, dataclass, field

import serde
import serde.json


@dataclass
class RawSmall:
    i: int
    s: str
    f: float
    b: bool


@dataclass
class RawMedium:
    i: int
    s: str
    f: float
    b: bool
    i2: int
    s2: str
    f2: float
    b2: bool
    i3: int
    s3: str
    f3: float
    b3: bool
    i4: int
    s4: str
    f4: float
    b4: bool
    i5: int
    s5: str
    f5: float
    b5: bool


@serde.serialize
@serde.deserialize
@dataclass
class SerdeSmall:
    i: int
    s: str
    f: float
    b: bool


@serde.serialize
@serde.deserialize
@dataclass
class SerdeMedium:
    i: int
    s: str
    f: float
    b: bool
    i2: int
    s2: str
    f2: float
    b2: bool
    i3: int
    s3: str
    f3: float
    b3: bool
    i4: int
    s4: str
    f4: float
    b4: bool
    i5: int
    s5: str
    f5: float
    b5: bool


@dataclasses_json.dataclass_json
@dataclass
class DJsonSmall:
    i: int
    s: str
    f: float
    b: bool


@dataclass
class DJSchemaSmall(dataclasses_jsonschema.JsonSchemaMixin):
    i: int
    s: str
    f: float
    b: bool


@dataclass
class MashumaroSmall(mashumaro.DataClassJSONMixin):
    i: int
    s: str
    f: float
    b: bool


@ix.ix
class IXSmall:
    i: int
    s: str
    f: float
    b: bool


@dataclasses_json.dataclass_json
@dataclass
class DJsonMedium:
    i: int
    s: str
    f: float
    b: bool
    i2: int
    s2: str
    f2: float
    b2: bool
    i3: int
    s3: str
    f3: float
    b3: bool
    i4: int
    s4: str
    f4: float
    b4: bool
    i5: int
    s5: str
    f5: float
    b5: bool


@dataclass
class DJSchemaMedium(dataclasses_jsonschema.JsonSchemaMixin):
    i: int
    s: str
    f: float
    b: bool
    i2: int
    s2: str
    f2: float
    b2: bool
    i3: int
    s3: str
    f3: float
    b3: bool
    i4: int
    s4: str
    f4: float
    b4: bool
    i5: int
    s5: str
    f5: float
    b5: bool


@dataclass
class MashumaroMedium(mashumaro.DataClassJSONMixin):
    i: int
    s: str
    f: float
    b: bool
    i2: int
    s2: str
    f2: float
    b2: bool
    i3: int
    s3: str
    f3: float
    b3: bool
    i4: int
    s4: str
    f4: float
    b4: bool
    i5: int
    s5: str
    f5: float
    b5: bool


@ix.ix
class IXMedium:
    i: int
    s: str
    f: float
    b: bool
    i2: int
    s2: str
    f2: float
    b2: bool
    i3: int
    s3: str
    f3: float
    b3: bool
    i4: int
    s4: str
    f4: float
    b4: bool
    i5: int
    s5: str
    f5: float
    b5: bool


@dataclass
class RawPriContainer:
    v: List[int] = field(default_factory=list)
    d: Dict[str, int] = field(default_factory=dict)
    t: Tuple[bool] = field(default_factory=tuple)


@serde.serialize
@serde.deserialize
@dataclass
class SerdePriContainer:
    v: List[int] = field(default_factory=list)
    d: Dict[str, int] = field(default_factory=dict)
    t: Tuple[bool] = field(default_factory=tuple)


@dataclasses_json.dataclass_json
@dataclass
class DJsonPriContainer:
    v: List[int] = field(default_factory=list)
    d: Dict[str, int] = field(default_factory=dict)
    t: Tuple[bool] = field(default_factory=tuple)


@dataclass
class DJSchemaPriContainer(dataclasses_jsonschema.JsonSchemaMixin):
    v: List[int] = field(default_factory=list)
    d: Dict[str, int] = field(default_factory=dict)
    t: Tuple[bool] = field(default_factory=tuple)


@dataclass
class MashmaroPriContainer(mashumaro.DataClassJSONMixin):
    v: List[int] = field(default_factory=list)
    d: Dict[str, int] = field(default_factory=dict)
    t: Tuple[bool] = field(default_factory=tuple)


json_sm = '{"i": 10, "s": "hoge", "f": 100.0, "b": true}'

json_md = ('{"i": 10, "s": "hoge", "f": 100.0, "b": true,'
           '"i2": 10, "s2": "hoge", "f2": 100.0, "b2": true,'
           '"i3": 10, "s3": "hoge", "f3": 100.0, "b3": true,'
           '"i4": 10, "s4": "hoge", "f4": 100.0, "b4": true,'
           '"i5": 10, "s5": "hoge", "f5": 100.0, "b5": true}')

json_pri_container = '{"v": [1, 2, 3, 4, 5], "d": {"hoge": 10, "fuga": 20}, "foo": 30, "t": [true, false, true]}'

ix_json_sm = f'[{json_sm}]'

ix_json_md = f'[{json_md}]'

args_sm = {'i': 10, 's': 'hoge', 'f': 100.0, 'b': True}


def profile(name, func, *args, **kwargs):
    if args:
        func = functools.partial(func, *args, **kwargs)
    times = timeit.repeat(func, number=10000, repeat=5)
    times = ', '.join([f'{t:.6f}' for t in times])
    print(f'{name:40s}\t{times}')


def de_raw_small():
    dct = json.loads(json_sm)
    return RawSmall(dct['i'], dct['s'], dct['f'], dct['b'])


def de_raw_medium():
    dct = json.loads(json_md)
    return RawMedium(dct['i'], dct['s'], dct['f'], dct['b'], dct['i2'], dct['s2'], dct['f2'], dct['b2'], dct['i3'],
                     dct['s3'], dct['f3'], dct['b3'], dct['i4'], dct['s4'], dct['f4'], dct['b4'], dct['i5'], dct['s5'],
                     dct['f5'], dct['b5'])


def de_raw_pri_container():
    dct = json.loads(json_pri_container)
    return RawPriContainer(dct['v'], dct['d'], dct['t'])


def se_raw(cls: Type, **kwargs):
    c = cls(**kwargs)
    return json.dumps(asdict(c))


def de_pyserde(cls: Type, data: str):
    return serde.json.from_json(cls, data)


def se_pyserde(cls: Type, **kwargs):
    return serde.json.to_json(cls(**kwargs))


def de_dataclasses_json(cls: Type, data: str):
    return cls.from_json(data)


def se_dataclasses_json(cls: Type, **kwargs):
    c = cls(**args_sm)
    return c.to_json()


def de_dataclasses_jsonschema(cls: Type, data: str):
    return cls.from_dict(json.loads(data))


def se_dataclasses_jsonschema(cls: Type, **kwargs):
    c = cls(**args_sm)
    return json.dumps(asdict(c))


def de_dacite(cls: Type, data: str):
    return dacite.from_dict(data_class=cls, data=json.loads(data))


def se_dacite(cls: Type, **kwargs):
    c = cls(**args_sm)
    return json.dumps(asdict(c))


def de_pavlova(cls: Type, data: str):
    return pavlova.Pavlova().from_mapping(json.loads(data), cls)


def se_pavlova(cls: Type, **kwargs):
    c = cls(**args_sm)
    return json.dumps(asdict(c))


def de_mashumaro(cls: Type, data: str):
    return cls.from_json(data)


def se_mashumaro(cls: Type, **kwargs):
    c = cls(**args_sm)
    return c.to_json()


def de_ix(cls: Type, data: str):
    return list(cls.from_jsons(data))[0]


def main():
    if len(sys.argv) >= 2:
        f = globals().get(sys.argv[1], None)
        if f:
            f()
    else:
        de_small()
        de_medium()
        de_pri_container()
        se_small()


def de_small():
    print('--- deserialize small ---')
    profile('raw', de_raw_small)
    profile('pyserde', de_pyserde, SerdeSmall, json_sm)
    profile('dacite', de_dacite, RawSmall, json_sm)
    profile('dataclasses_json', de_dataclasses_json, DJsonSmall, json_sm)
    profile('dataclasses_jsonschema', de_dataclasses_jsonschema, DJSchemaSmall, json_sm)
    profile('pavlova', de_pavlova, RawSmall, json_sm)
    profile('mashumaro', de_mashumaro, MashumaroSmall, json_sm)
    profile('ix', de_ix, IXSmall, ix_json_sm)


def de_medium():
    print('--- deserialize medium ---')
    profile('raw', de_raw_medium)
    profile('pyserde', de_pyserde, SerdeMedium, json_md)
    profile('dacite', de_dacite, RawMedium, json_md)
    profile('dataclasses_json', de_dataclasses_json, DJsonMedium, json_md)
    profile('dataclasses_jsonschema', de_dataclasses_jsonschema, DJSchemaMedium, json_md)
    profile('pavlova', de_pavlova, RawMedium, json_md)
    profile('mashumaro', de_mashumaro, MashumaroMedium, json_md)
    profile('ix', de_ix, IXMedium, ix_json_md)


def de_pri_container():
    print('--- deserialize primitive containers ---')
    profile('raw', de_raw_pri_container)
    profile('pyserde', de_pyserde, SerdePriContainer, json_pri_container)
    # profile('dacite', de_dacite, RawPriContainer, json_pri_container)
    profile('dataclasses_json', de_dataclasses_json, DJsonPriContainer, json_pri_container)
    # profile('dataclasses_jsonschema', de_dataclasses_jsonschema, DJSchemaPriContainer, json_pri_container)
    # profile('pavlova', de_pavlova, RawPriContainer, json_pri_container)
    profile('mashumaro', de_mashumaro, MashmaroPriContainer, json_pri_container)


def se_small():
    print('--- serialize small ---')
    profile('raw', se_raw, RawSmall, **args_sm)
    profile('pyserde', se_pyserde, SerdeSmall, **args_sm)
    profile('dacite', se_dacite, RawSmall, **args_sm)
    profile('pavlova', se_pavlova, RawSmall, **args_sm)
    profile('dataclasses_json', se_dataclasses_json, DJsonSmall, **args_sm)
    profile('dataclasses_jsonschema', se_dataclasses_jsonschema, DJSchemaSmall, **args_sm)
    profile('mashumaro', se_mashumaro, MashumaroSmall, **args_sm)


if __name__ == '__main__':
    main()
