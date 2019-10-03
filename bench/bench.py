"""
bench.py - Benchmarking pyserde.

Benchmarking pyserde as well as

1. raw
Without any dataclass based library, manually serialize and deserialize.
`raw` should be fastest in theory, However it is too verbose to write in
production grade codebase at the same time. pyserde's performance goal is
to run as fast as `raw`.
"""
import functools
import json
import sys
import timeit
from dataclasses import dataclass

import click

import dacite_class as da
import data
import dataclasses_class as dc
import dataclasses_json_class as dj
import mashumaro_class as mc
import pyserde_class as ps
import raw


@dataclass
class Opt:
    """
    Benchmark options.
    """

    full: bool


@dataclass
class Bencher:
    number: int = 10000
    repeat: int = 5

    def run(self, name, func, *args, expected=None, **kwargs):
        """
        Run benchmark.
        """
        if args or kwargs:
            f = functools.partial(func, *args, **kwargs)
        else:
            f = func

        # Evaluate result only once.
        if expected:
            actual = f()
            if actual != expected:
                click.echo((f'AssertionError\n' f'Expected:\n{expected}\n' f'Actual:\n{actual}'))
                sys.exit(1)

        times = timeit.repeat(f, number=self.number, repeat=self.repeat)
        times = ', '.join([f'{t:.6f}' for t in times])
        click.echo(f'{name:40s}\t{times}')


def de_small(opt: Opt):
    click.echo('--- deserialize small ---')
    bench = Bencher()
    bench.run('raw', raw.de_small)
    bench.run('pyserde', ps.de, ps.Small, data.SMALL)
    if opt.full:
        bench.run('dacite', da.de, raw.Small, data.SMALL)
        bench.run('dataclasses_json', dj.de, dj.Small, data.SMALL)
        bench.run('mashumaro', mc.de, mc.Small, data.SMALL)


def de_medium(opt: Opt):
    click.echo('--- deserialize medium (number=1000) ---')
    bench = Bencher(number=1000)
    bench.run('raw', raw.de_medium)
    bench.run('pyserde', ps.de, ps.Medium, data.MEDIUM)
    if opt.full:
        bench.run('dacite', da.de, ps.Medium, data.MEDIUM)
        bench.run('dataclasses_json', dj.de, dj.Medium, data.MEDIUM)
        bench.run('mashumaro', mc.de, mc.Medium, data.MEDIUM)


def se_small(opt: Opt):
    click.echo('--- serialize small ---')
    bench = Bencher()
    bench.run('raw', raw.se_small, raw.Small, **data.args_sm)
    bench.run('dataclass', dc.se, raw.Small, **data.args_sm)
    bench.run('pyserde', ps.se, ps.Small, **data.args_sm)
    if opt.full:
        bench.run('dacite', da.se, ps.Small, **data.args_sm)
        bench.run('dataclasses_json', dj.se, dj.Small, **data.args_sm)
        bench.run('mashumaro', mc.se, mc.Small, **data.args_sm)


def astuple_small(opt: Opt):
    click.echo('--- astuple small ---')
    bench = Bencher()
    exp = tuple(json.loads(data.SMALL).values())
    bench.run('raw', raw.astuple_small, raw.Small(*exp), expected=exp)
    bench.run('dataclass', dc.astuple, dc.Small(*exp), expected=exp)
    bench.run('pyserde', ps.astuple, ps.Small(*exp), expected=exp)


def astuple_medium(opt: Opt):
    click.echo('--- astuple medium (number=1000) ---')
    bench = Bencher(number=1000)
    exp = data.MEDIUM_TUPLE
    bench.run('raw', raw.astuple_medium, raw.Medium([dc.Small(*data.SMALL_TUPLE)] * 50), expected=exp)
    bench.run('dataclass', dc.astuple, dc.Medium([dc.Small(*data.SMALL_TUPLE)] * 50), expected=exp)
    bench.run('pyserde', ps.astuple, ps.Medium([ps.Small(*data.SMALL_TUPLE)] * 50), expected=exp)


def asdict(opt: Opt):
    click.echo('--- asdict small ---')
    bench = Bencher()
    exp = {'i': 10, 's': 'foo', 'f': 100.0, 'b': True}
    bench.run('dataclass', dc.asdict, dc.Small(10, 'foo', 100.0, True), expected=exp)
    bench.run('pyserde', ps.asdict, ps.Small(10, 'foo', 100.0, True), expected=exp)


@click.command()
@click.option('-f', '--full', type=bool, is_flag=True, default=False, help='Run full benchmark tests.')
@click.option('-t', '--test', type=str, default='', help='Run specified test case only.')
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
            click.echo(f'Test not found: \'{test}\'')
            sys.exit(1)
    else:
        de_small(opt)
        de_medium(opt)
        se_small(opt)
        astuple_small(opt)
        astuple_medium(opt)
        asdict(opt)


if __name__ == '__main__':
    main()
