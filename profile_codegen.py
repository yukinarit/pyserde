from serde import serde, serialize, deserialize
from serde.json import from_json, to_json
from dataclasses import dataclass
from beartype import beartype
import cProfile
import pstats


@beartype
@dataclass
class FewFields:
    a: int
    b: float
    c: str
    d: bool


@beartype
@dataclass
class ManyFields:
    a1: int
    a2: int
    a3: int
    a4: int
    a5: int
    a6: int
    a7: int
    a8: int
    a9: int
    a10: int
    a11: int
    a12: int
    a13: int
    a14: int
    a15: int
    a16: int
    a17: int
    a18: int
    a19: int
    a20: int
    b1: int
    b2: int
    b3: int
    b4: int
    b5: int
    b6: int
    b7: int
    b8: int
    b9: int
    b10: int
    b11: int
    b12: int
    b13: int
    b14: int
    b15: int
    b16: int
    b17: int
    b18: int
    b19: int
    b20: int
    c1: int
    c2: int
    c3: int
    c4: int
    c5: int
    c6: int
    c7: int
    c8: int
    c9: int
    c10: int
    c11: int
    c12: int
    c13: int
    c14: int
    c15: int
    c16: int
    c17: int
    c18: int
    c19: int
    c20: int
    d1: int
    d2: int
    d3: int
    d4: int
    d5: int
    d6: int
    d7: int
    d8: int
    d9: int
    d10: int
    d11: int
    d12: int
    d13: int
    d14: int
    d15: int
    d16: int
    d17: int
    d18: int
    d19: int
    d20: int


def profile_few_fields() -> None:
    for n in range(100):
        serde(FewFields)


def profile_many_fields() -> None:
    for n in range(100):
        serde(ManyFields)


cProfile.run("profile_few_fields()", filename="profile_results.prof")
stats = pstats.Stats("profile_results.prof")
stats.sort_stats("tottime").print_stats(20)

cProfile.run("profile_many_fields()", filename="profile_results.prof")
stats = pstats.Stats("profile_results.prof")
stats.sort_stats("tottime").print_stats(20)
