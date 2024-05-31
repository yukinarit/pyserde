import jedi


def test_jedi() -> None:
    source = """
from serde import serde

@serde
class Foo:
    a: int
    b: float
    c: str
    baz: bool

foo = Foo(10, 100.0, "foo", True)
"""
    source_completion = source + "\n" + "foo."
    jedi_script = jedi.Script(source_completion, path="foo.py")
    completions = jedi_script.complete(9, len("foo."))
    completions = [comp.name for comp in completions]
    assert "a" in completions
    assert "b" in completions
    assert "c" in completions
