"""
bench.py - Benchmarking pyserde.
"""
import json
import timeit
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path
from platform import python_implementation
from typing import Any, Callable, Dict, List, Tuple, Union

import click

import data
import dataclasses_class as dc
import pyserde_class as ps  # noqa: F401
import raw  # noqa: F401
from runner import Size

try:
    if python_implementation() != 'PyPy':
        import dacite_class as da  # noqa: F401
        import mashumaro_class as mc  # noqa: F401
        import marshmallow_class as ms  # noqa: F401
        import attrs_class as at  # noqa: F401
        import cattrs_class as ca  # noqa: F401
        import dataclasses_json_class as dj  # noqa: F401
        import pydantic_class as pd  # noqa: F401
        import seaborn as sns
        import matplotlib.pyplot as plt
        import numpy as np
except ImportError:
    pass


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

    def run(self, name, func, expected=None, **kwargs):
        """
        Run benchmark.
        """
        if kwargs:
            f = partial(func, **kwargs)
        else:
            f = func
        if not f:
            return

        # Evaluate result only once.
        if expected:
            actual = f()
            if callable(expected):
                expected(actual)
            else:
                assert actual == expected, f'Expected: {expected}, Actual: {actual}'

        times = timeit.repeat(f, number=self.number, repeat=self.repeat)
        self.result.append((name, sum(times) / len(times)))
        times = ', '.join([f'{t:.6f}' for t in times])
        click.echo(f'{name:40s}\t{times}')
        self.draw_chart()

    def draw_chart(self):
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
            plt.xticks(rotation=20)
            plt.savefig(str(self.opt.output / f'{self.name}.png'))
            plt.close()


runners_base = ('raw', 'dc', 'ps')

runners_extra = ('da', 'mc', 'ms', 'at', 'ca', 'dj', 'pd')


def run(opt: Opt, name: str, tc: 'TestCase'):
    """
    Run benchmark.
    """
    bench = Bencher(f'{name}-{tc.size.name.lower()}', opt, tc.number)
    click.echo(f'--- {bench.name} ---')
    runners = runners_base + runners_extra if opt.full else runners_base
    for runner_name in runners:
        runner = globals()[runner_name].new(tc.size)
        bench.run(runner.name, getattr(runner, name), tc.expected)


@dataclass
class TestCase:
    size: Size
    expected: Union[Any, Callable[[Any], bool]]
    number: int

    @classmethod
    def make(cls, size: Size, expected=None, number=10000) -> Dict[str, 'TestCase']:
        return {size: TestCase(size, expected, number)}


def equals_small(x):
    y = dc.SMALL
    assert x.i == y.i and x.s == y.s and x.f == y.f and x.b == y.b, f'Expected: {x}, Actual: {y}'


def equals_medium(x):
    y = dc.MEDIUM
    for (xs, ys) in zip(x.inner, y.inner):
        assert xs.i == xs.i and xs.s == ys.s and xs.f == ys.f and xs.b == ys.b, f'Expected: {x}, Actual: {y}'


TESTCASES = {
    'se': {
        **TestCase.make(Size.Small, lambda x: json.loads(x) == json.loads(data.SMALL)),
        **TestCase.make(Size.Medium, lambda x: json.loads(x) == json.loads(data.MEDIUM), number=500),
    },
    'de': {**TestCase.make(Size.Small, equals_small), **TestCase.make(Size.Medium, equals_medium, number=500)},
    'astuple': {**TestCase.make(Size.Small, data.SMALL_TUPLE), **TestCase.make(Size.Medium, number=500)},
    'asdict': {**TestCase.make(Size.Small, data.SMALL_DICT), **TestCase.make(Size.Medium, number=500)},
}


@click.command()
@click.option('-f', '--full', type=bool, is_flag=True, default=False, help='Run full benchmark tests.')
@click.option('-t', '--test', default='', help='Run specified test case only.')
@click.option('-c', '--chart', type=bool, is_flag=True, default=False, help='Draw barcharts of benchmark results.')
@click.option(
    '-o', '--output', default='charts', callback=lambda _, __, p: Path(p), help='Output directory for charts.'
)
def main(full: bool, test: str, chart: bool, output: Path):
    """
    bench.py - Benchmarking pyserde and other libraries.
    """
    opt = Opt(full, chart, output)
    tests = (test,) if test else TESTCASES
    for test in tests:
        for size in Size:
            try:
                tc = TESTCASES[test][size]
                run(opt, test, tc)
            except KeyError:
                pass


if __name__ == '__main__':
    main()
