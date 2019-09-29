"""
bench.py - Benchmarking pyserde.

Benchmarking pyserde as well as

1. raw
Without any dataclass based library, manually serialize and deserialize.
`raw` should be fastest in theory, However it is too verbose to write in
production grade codebase at the same time. pyserde's performance goal is
to run as fast as `raw`.
"""
import click
import functools
import timeit
from dataclasses import dataclass

import dacite_class
import mashumaro_class as mc
import dataclasses_json_class as dj
import raw
import pyserde_class as ps
from tests.data import Pri
from data import json_sm, json_md, args_sm, json_pri_container


@dataclass
class Opt:
    """
    Benchmark options.
    """
    full: bool


def profile(name, func, *args, expected=None, **kwargs):
    """
    Run benchmark.
    """
    if args:
        func = functools.partial(func, *args, **kwargs)
    if expected:

        def assert_func(*args, **kwargs):
            assert func(*args, **kwargs) == expected

        f = assert_func
    else:
        f = func
    times = timeit.repeat(f, number=10000, repeat=5)
    times = ', '.join([f'{t:.6f}' for t in times])
    click.echo(f'{name:40s}\t{times}')


def de_small(opt: Opt):
    click.echo('--- deserialize small ---')
    profile('raw', raw.de_raw_small)
    profile('pyserde', ps.de_pyserde, ps.SerdeSmall, json_sm)
    if opt.full:
        profile('dacite', dacite_class.de, Pri, json_sm)
        profile('dataclasses_json', dj.de_dataclasses_json, dj.DJsonSmall, json_sm)
        profile('mashumaro', mc.de_mashumaro, mc.MashumaroSmall, json_sm)


def de_medium(opt: Opt):
    click.echo('--- deserialize medium ---')
    profile('raw', raw.de_raw_medium)
    profile('pyserde', ps.de_pyserde, ps.SerdeMedium, json_md)
    if opt.full:
        profile('dacite', dacite_class.de, raw.RawMedium, json_md)
        profile('dataclasses_json', dj.de_dataclasses_json, dj.DJsonMedium, json_md)
        profile('mashumaro', mc.de_mashumaro, mc.MashumaroMedium, json_md)


def de_pri_container(opt: Opt):
    click.echo('--- deserialize primitive containers ---')
    profile('raw', raw.de_raw_pri_container)
    profile('pyserde', ps.de_pyserde, ps.SerdePriContainer, json_pri_container)
    if opt.full:
        profile('dacite', dacite_class.de, raw.RawPriContainer, json_pri_container)
        profile('dataclasses_json', dj.de_dataclasses_json, dj.DJsonPriContainer, json_pri_container)
        profile('mashumaro', mc.de_mashumaro, mc.MashmaroPriContainer, json_pri_container)


def se_small(opt: Opt):
    click.echo('--- serialize small ---')
    profile('raw', raw.se_raw_small, Pri, **args_sm)
    profile('dataclass', raw.se_dataclass, Pri, **args_sm)
    profile('pyserde', ps.se_pyserde, ps.SerdeSmall, **args_sm)
    if opt.full:
        profile('dacite', dacite_class.se_dacite, Pri, **args_sm)
        profile('dataclasses_json', dj.se_dataclasses_json, dj.DJsonSmall, **args_sm)
        profile('mashumaro', mc.se_mashumaro, mc.MashumaroSmall, **args_sm)


def se_astuple(opt: Opt):
    click.echo('--- astuple small ---')
    exp = (10, 'foo', 100.0, True)
    profile('raw', raw.astuple_raw, Pri(10, 'foo', 100.0, True), expected=exp)
    profile('dataclass', raw.astuple_dataclass, Pri(10, 'foo', 100.0, True), expected=exp)
    profile('pyserde', ps.astuple_pyserde, Pri(10, 'foo', 100.0, True), expected=exp)

    click.echo('--- astuple medium ---')
    exp = (
        10,
        'foo',
        100.0,
        True,
        10,
        'foo',
        100.0,
        True,
        10,
        'foo',
        100.0,
        True,
        10,
        'foo',
        100.0,
        True,
        10,
        'foo',
        100.0,
        True,
    )
    md = raw.RawMedium(
        10,
        'foo',
        100.0,
        True,
        10,
        'foo',
        100.0,
        True,
        10,
        'foo',
        100.0,
        True,
        10,
        'foo',
        100.0,
        True,
        10,
        'foo',
        100.0,
        True,
    )
    sm = ps.SerdeMedium(
        10,
        'foo',
        100.0,
        True,
        10,
        'foo',
        100.0,
        True,
        10,
        'foo',
        100.0,
        True,
        10,
        'foo',
        100.0,
        True,
        10,
        'foo',
        100.0,
        True,
    )
    profile('raw', raw.astuple_raw, md, expected=exp)
    profile('pyserde', ps.astuple_pyserde, sm, expected=exp)


def se_asdict(opt: Opt):
    click.echo('--- asdict small ---')
    exp = {'i': 10, 's': 'foo', 'f': 100.0, 'b': True}
    profile('raw', raw.asdict_raw, Pri(10, 'foo', 100.0, True), expected=exp)
    profile('pyserde', ps.asdict_pyserde, ps.SerdeSmall(10, 'foo', 100.0, True), expected=exp)


@click.command()
@click.option('-f', '--full', type=bool, is_flag=True, default=False, help='Run full benchmark tests.')
@click.option('-t', '--test', type=str, default='', help='Specify test case to run.')
def main(full: bool, test: str):
    """
    bench.py - Benchmarking pyserde.
    """
    opt = Opt(full)
    if test:
        f = globals().get(test, None)
        if f:
            f(opt)
    else:
        de_small(opt)
        de_medium(opt)
        # de_pri_container(opt)
        se_small(opt)
        se_astuple(opt)
        se_asdict(opt)


if __name__ == '__main__':
    main()
