"""
skip_if_none.py

Demonstrates field- and class-level skip_if_none.

Usage:
    $ uv sync
    $ uv run python skip_if_none.py
"""

from serde import serde, field
from serde.json import to_json


@serde
class Profile:
    nickname: str | None = field(default=None, skip_if_none=True)
    bio: str | None = field(default=None, skip_if_none=False)  # kept even when None


@serde(skip_if_none=True)
class Account:
    profile: Profile | None = None
    email: str | None = None
    flags: dict[str, bool] | None = None


def main() -> None:
    # Field-level skip_if_none
    print(to_json(Profile()))
    print(to_json(Profile("ash")))

    # Class-level skip_if_none with nested dataclass
    print(to_json(Account()))
    print(to_json(Account(profile=Profile("misty"), email="misty@example.com")))
    print(to_json(Account(profile=Profile(bio="trainer"))))


if __name__ == "__main__":
    main()
