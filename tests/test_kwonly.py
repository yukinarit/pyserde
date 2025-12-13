from dataclasses import dataclass, field

from serde import deserialize, from_dict


def test_simple() -> None:
    @deserialize
    @dataclass(kw_only=True)
    class Hello:
        a: str

    assert Hello(a="ok") == from_dict(Hello, {"a": "ok"})


def test_inheritance() -> None:
    @dataclass(kw_only=True)
    class Friend:
        name: str = "MyFriend"

    @dataclass(kw_only=True)
    class Parent:
        child_val: str | None

    @dataclass(kw_only=True)
    class Child(Parent):
        value: int = 42
        friend: Friend = field(default_factory=Friend)

    # check with defaults
    assert Child(child_val="test") == from_dict(Child, {"child_val": "test"})

    # check without defaults
    assert Child(child_val="test", value=34, friend=Friend(name="my_friend")) == from_dict(
        Child, {"child_val": "test", "value": 34, "friend": {"name": "my_friend"}}
    )
