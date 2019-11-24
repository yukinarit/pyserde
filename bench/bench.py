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
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple

import click

import dacite_class as da
import data
import dataclasses_class as dc
# import dataclasses_json_class as dj
import mashumaro_class as mc
import matplotlib.pyplot as plt
import numpy as np
import pyserde_class as ps
import raw
import seaborn as sns


@dataclass
class Opt:
    """
    Benchmark options.
    """

    full: bool
    chart: bool
    output: Path

    def __post_init__(self):
        if not self.output.exists():
            self.output.mkdir()


@dataclass
class Bencher:
    name: str
    opt: Opt
    number: int = 10000
    repeat: int = 5
    result: List[Tuple[str, float]] = field(default_factory=list)

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
        self.result.append((name, sum(times) / len(times)))
        times = ', '.join([f'{t:.6f}' for t in times])
        click.echo(f'{name:40s}\t{times}')

    def __del__(self):
        if self.opt.chart:
            x = np.array([r[0] for r in self.result])
            y = np.array([r[1] for r in self.result])
            chart = sns.barplot(x=x, y=y, palette="rocket")
            chart.set(ylabel=f'Elapsed time for {self.number} requests [sec]')
            for p in chart.patches:
                chart.annotate(
                    format(p.get_height(), '.4f'),
                    (p.get_x() + p.get_width() / 2.0, p.get_height()),
                    ha='center',
                    va='center',
                    xytext=(0, 10),
                    textcoords='offset points',
                )
            plt.savefig(str(self.opt.output / f'{self.name}.png'))
            plt.close()


def de_small(opt: Opt):
    bench = Bencher('deserialize_small', opt)
    click.echo(f'--- {bench.name} ---')
    bench.run('raw', raw.de_small)
    bench.run('pyserde', ps.de, ps.Small, data.SMALL)
    if opt.full:
        bench.run('dacite', da.de, raw.Small, data.SMALL)
        # bench.run('dataclasses_json', dj.de, dj.Small, data.SMALL)
        bench.run('mashumaro', mc.de, mc.Small, data.SMALL)


def de_medium(opt: Opt):
    bench = Bencher('deserialize_medium', opt, number=1000)
    click.echo(f'--- {bench.name} ---')
    bench.run('raw', raw.de_medium)
    bench.run('pyserde', ps.de, ps.Medium, data.MEDIUM)
    if opt.full:
        bench.run('dacite', da.de, ps.Medium, data.MEDIUM)
        # bench.run('dataclasses_json', dj.de, dj.Medium, data.MEDIUM)
        bench.run('mashumaro', mc.de, mc.Medium, data.MEDIUM)


def se_small(opt: Opt):
    bench = Bencher('serialize_small', opt)
    click.echo(f'--- {bench.name} ---')
    bench.run('raw', raw.se_small, raw.Small, **data.args_sm)
    bench.run('pyserde', ps.se, ps.Small, **data.args_sm)
    if opt.full:
        bench.run('dacite', da.se, ps.Small, **data.args_sm)
        # bench.run('dataclasses_json', dj.se, dj.Small, **data.args_sm)
        bench.run('mashumaro', mc.se, mc.Small, **data.args_sm)


def astuple_small(opt: Opt):
    bench = Bencher('astuple_small', opt)
    click.echo(f'--- {bench.name} ---')
    exp = tuple(json.loads(data.SMALL).values())
    bench.run('raw', raw.astuple_small, raw.Small(*exp), expected=exp)
    bench.run('dataclass', dc.astuple, dc.Small(*exp), expected=exp)
    bench.run('pyserde', ps.astuple, ps.Small(*exp), expected=exp)


def astuple_medium(opt: Opt):
    bench = Bencher('astuple medium', opt, number=1000)
    click.echo(f'--- {bench.name} ---')
    exp = data.MEDIUM_TUPLE
    bench.run('raw', raw.astuple_medium, raw.Medium([dc.Small(*data.SMALL_TUPLE)] * 50), expected=exp)
    bench.run('dataclass', dc.astuple, dc.Medium([dc.Small(*data.SMALL_TUPLE)] * 50), expected=exp)
    bench.run('pyserde', ps.astuple, ps.Medium([ps.Small(*data.SMALL_TUPLE)] * 50), expected=exp)


def asdict(opt: Opt):
    bench = Bencher('asdict_small', opt)
    click.echo(f'--- {bench.name} ---')
    exp = {'i': 10, 's': 'foo', 'f': 100.0, 'b': True}
    bench.run('dataclass', dc.asdict, dc.Small(10, 'foo', 100.0, True), expected=exp)
    bench.run('pyserde', ps.asdict, ps.Small(10, 'foo', 100.0, True), expected=exp)


@click.command()
@click.option('-f', '--full', type=bool, is_flag=True, default=False, help='Run full benchmark tests.')
@click.option('-t', '--test', default='', help='Run specified test case only.')
@click.option('-c', '--chart', type=bool, is_flag=True, default=False, help='Draw barcharts of benchmark results.')
@click.option(
    '-o', '--output', default='charts', callback=lambda _, __, p: Path(p), help='Output directory for charts.'
)
def main(full: bool, test: str, chart: bool, output: Path):
    """
    bench.py - Benchmarking pyserde.
    """
    opt = Opt(full, chart, output)
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
