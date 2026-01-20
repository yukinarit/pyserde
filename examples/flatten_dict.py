from typing import Any

from serde import field, serde
from serde.json import from_json, to_json


@serde
class User:
    """Example with flattened dict to capture extra fields."""

    id: int
    name: str
    extra: dict[str, Any] = field(flatten=True, default_factory=dict)


@serde
class Config:
    """Example combining regular fields with flattened dict."""

    version: str
    debug: bool = False
    settings: dict[str, Any] = field(flatten=True, default_factory=dict)


@serde
class Metadata:
    """Example using bare dict (without type parameters)."""

    title: str
    tags: dict = field(flatten=True, default_factory=dict)


def main() -> None:
    print("=== Basic Flatten Dict Example ===")

    # Deserialization - extra fields captured in dict
    json_with_extra = '{"id": 1, "name": "Alice", "role": "admin", "active": true}'
    user = from_json(User, json_with_extra)
    print(f"From Json: {user}")
    print(f"  id: {user.id}")
    print(f"  name: {user.name}")
    print(f"  extra: {user.extra}")

    print()

    # Serialization - dict contents merged back
    user2 = User(id=2, name="Bob", extra={"department": "Engineering", "level": 5})
    print(f"To Json: {to_json(user2)}")

    print()
    print("=== Config Example ===")

    # Config with various extra settings
    config_json = '{"version": "1.0", "debug": true, "max_connections": 100, "timeout": 30}'
    config = from_json(Config, config_json)
    print(f"From Json: {config}")
    print(f"  version: {config.version}")
    print(f"  debug: {config.debug}")
    print(f"  settings: {config.settings}")

    # Round-trip
    print(f"Round-trip: {to_json(config)}")

    print()
    print("=== Bare Dict Example ===")

    # Bare dict (without type parameters) also works
    meta_json = '{"title": "Article", "author": "Alice", "published": "2024-01-01"}'
    meta = from_json(Metadata, meta_json)
    print(f"From Json: {meta}")
    print(f"  title: {meta.title}")
    print(f"  tags: {meta.tags}")
    print(f"To Json: {to_json(meta)}")


if __name__ == "__main__":
    main()
