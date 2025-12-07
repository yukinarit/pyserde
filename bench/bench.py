"""
bench.py - Benchmarking pyserde.
"""

from __future__ import annotations
import json
import timeit
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path
from platform import python_implementation
from collections.abc import Callable
from typing import Any, Optional, Union

import click
import data
import dataclasses_class as dc
import pyserde_class as ps  # noqa: F401
import pyserde_nt_class as pn  # noqa: F401
import raw  # noqa: F401
from runner import Size

try:
    if python_implementation() != "PyPy":
        import attrs_class as at  # noqa: F401
        import cattrs_class as ca  # noqa: F401
        import dacite_class as da  # noqa: F401
        import marshmallow_class as ms  # noqa: F401
        import mashumaro_class as mc  # noqa: F401
        import pydantic_class as pd  # noqa: F401
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

    def __post_init__(self) -> None:
        if not self.output.exists():
            self.output.mkdir()


@dataclass
class Bencher:
    name: str
    opt: Opt
    number: int = 10000
    repeat: int = 5
    result: list[tuple[str, float]] = field(default_factory=list)

    def run(
        self,
        name: str,
        func: Optional[Callable[..., Any]],
        expected: Optional[Union[Any, Callable[[Any], bool]]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Run benchmark.
        """
        if not func:
            return

        f: Callable[[], Any]
        if kwargs:
            f = partial(func, **kwargs)
        else:
            f = func

        # Evaluate result only once.
        if expected:
            actual = f()
            if callable(expected):
                expected(actual)
            else:
                assert actual == expected, f"Expected: {expected}, Actual: {actual}"

        times = timeit.repeat(f, number=self.number, repeat=self.repeat)
        self.result.append((name, sum(times) / len(times)))
        times_str = ", ".join([f"{t:.6f}" for t in times])
        click.echo(f"{name:40s}\t{times_str}")
        self.draw_chart()

    def draw_chart(self) -> None:
        if self.opt.chart:
            try:
                import matplotlib.pyplot as plt
                import numpy as np
                import seaborn as sns  # type: ignore[import]

                x = np.array([r[0] for r in self.result])
                y = np.array([r[1] for r in self.result])
                chart = sns.barplot(x=x, y=y, palette="rocket")
                chart.set(ylabel=f"Elapsed time for {self.number} requests [sec]")
                for p in chart.patches:
                    chart.annotate(
                        format(p.get_height(), ".4f"),
                        (p.get_x() + p.get_width() / 2.0, p.get_height()),
                        ha="center",
                        va="center",
                        xytext=(0, 10),
                        textcoords="offset points",
                    )
                plt.xticks(rotation=20)
                plt.savefig(str(self.opt.output / f"{self.name}.png"))
                plt.close()
            except ImportError:
                pass


runners_base = ("raw", "dc", "ps", "pn")

runners_extra = ("da", "mc", "ms", "at", "ca", "pd")


def run(opt: Opt, name: str, tc: TestCase) -> None:
    """
    Run benchmark.
    """
    bench = Bencher(f"{name}-{tc.size.name.lower()}", opt, tc.number)
    click.echo(f"--- {bench.name} ---")
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
    def make(cls, size: Size, expected: Any = None, number: int = 10000) -> dict[Size, TestCase]:
        return {size: TestCase(size, expected, number)}


def equals_small(x: Any) -> None:
    y = dc.SMALL
    assert x.i == y.i and x.s == y.s and x.f == y.f and x.b == y.b, f"Expected: {x}, Actual: {y}"


def equals_medium(x: Any) -> None:
    y = dc.MEDIUM
    for xs, ys in zip(x.inner, y.inner, strict=True):
        assert (
            xs.i == xs.i and xs.s == ys.s and xs.f == ys.f and xs.b == ys.b
        ), f"Expected: {x}, Actual: {y}"


def equals_large(x: Any) -> None:
    """Validate large deserialized data structure"""
    # Use different reference based on the library type
    if hasattr(type(x), "model_fields"):  # Pydantic model
        try:
            import pydantic_class as pd

            y = pd.LARGE
        except ImportError:
            y = ps.LARGE
    else:
        y = ps.LARGE

    assert (
        x.customer_id == y.customer_id
    ), f"Customer ID mismatch: {x.customer_id} != {y.customer_id}"
    assert x.name == y.name, f"Name mismatch: {x.name} != {y.name}"
    assert x.email == y.email, f"Email mismatch: {x.email} != {y.email}"
    assert len(x.items_list) == len(
        y.items_list
    ), f"Items list length mismatch: {len(x.items_list)} != {len(y.items_list)}"
    assert len(x.nested_data) == len(
        y.nested_data
    ), f"Nested data keys mismatch: {len(x.nested_data)} != {len(y.nested_data)}"
    assert (
        x.loyalty_points == y.loyalty_points
    ), f"Loyalty points mismatch: {x.loyalty_points} != {y.loyalty_points}"
    assert x.created_at == y.created_at, f"Created at mismatch: {x.created_at} != {y.created_at}"

    # Validate preferences
    assert x.preferences["theme"] == y.preferences["theme"], "Theme preference mismatch"
    assert (
        x.preferences["notifications"] == y.preferences["notifications"]
    ), "Notifications preference mismatch"

    # Validate nested data structure
    assert "category_1" in x.nested_data, "category_1 not found in nested_data"
    assert (
        len(x.nested_data["category_1"]) == 50
    ), f"category_1 length mismatch: {len(x.nested_data['category_1'])}"


TESTCASES = {
    "se": {
        **TestCase.make(Size.Small, lambda x: json.loads(x) == json.loads(data.SMALL)),
        **TestCase.make(
            Size.Medium, lambda x: json.loads(x) == json.loads(data.MEDIUM), number=500
        ),
        **TestCase.make(Size.Large, lambda x: json.loads(x) == json.loads(data.LARGE), number=100),
    },
    "de": {
        **TestCase.make(Size.Small, equals_small),
        **TestCase.make(Size.Medium, equals_medium, number=500),
        **TestCase.make(Size.Large, equals_large, number=100),
    },
    "astuple": {
        **TestCase.make(Size.Small, data.SMALL_TUPLE),
        **TestCase.make(Size.Medium, number=500),
        **TestCase.make(Size.Large, number=100),
    },
    "asdict": {
        **TestCase.make(Size.Small, data.SMALL_DICT),
        **TestCase.make(Size.Medium, number=500),
        **TestCase.make(Size.Large, number=100),
    },
}


@click.command()
@click.option(
    "-f", "--full", type=bool, is_flag=True, default=False, help="Run full benchmark tests."
)
@click.option("-t", "--test", default="", help="Run specified test case only.")
@click.option(
    "-c",
    "--chart",
    type=bool,
    is_flag=True,
    default=False,
    help="Draw barcharts of benchmark results.",
)
@click.option(
    "-o",
    "--output",
    default="charts",
    callback=lambda _, __, p: Path(p),
    help="Output directory for charts.",
)
def main(full: bool, test: str, chart: bool, output: Path) -> None:
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


if __name__ == "__main__":
    main()  # pyright: ignore[reportCallIssue]
