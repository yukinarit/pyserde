"""
Demonstrate skip_serializing and skip_deserializing field attributes.

Usage:
    $ uv sync
    $ uv run python skip_serializing_deserializing.py
"""

from serde import field, serde
from serde.json import from_json, to_json


@serde
class Credentials:
    user: str
    # Do not emit tokens in serialized output, but allow them on input.
    token: str = field(skip_serializing=True)


@serde
class Profile:
    username: str
    # Filled during runtime; ignore incoming data and use default.
    session_id: str = field(default="(generated)", skip_deserializing=True)


def main() -> None:
    creds = Credentials("ash", "secret-token")
    print("Serialized credentials (token omitted):", to_json(creds))

    creds_in = from_json(Credentials, '{"user": "misty", "token": "water"}')
    print("Deserialized credentials include token:", creds_in)

    profile_in = from_json(Profile, '{"username": "brock", "session_id": "client-sent"}')
    print("Session id is kept at default:", profile_in)

    profile = Profile("ash")
    print("Serialized profile keeps session_id:", to_json(profile))


if __name__ == "__main__":
    main()
