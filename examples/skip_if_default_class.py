"""
skip_if_default_class.py

Demonstrates class-level skip_if_default setting.

Usage:
    $ uv sync
    $ uv run python skip_if_default_class.py
"""

from serde import serde, field
from serde.json import to_json


@serde(skip_if_default=True)
class Settings:
    theme: str = "light"
    retries: int = 3
    api_key: str | None = None


@serde(skip_if_default=True)
class NestedSettings:
    parent: Settings = field(default_factory=Settings)
    enabled: bool = True


def main() -> None:
    # All default-valued fields are omitted.
    print(to_json(Settings()))

    # Non-default value is kept.
    print(to_json(Settings(api_key="secret", retries=5)))

    # Nested class respects class-level defaults too (defaults disappear).
    print(to_json(NestedSettings()))
    print(to_json(NestedSettings(Settings(api_key="abc123"))))


if __name__ == "__main__":
    main()
