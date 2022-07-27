"""
Test datetime types.
Particulary checks if different file formats (toml, yaml, and json)
correctly handle datetime types in their own way.
"""
from datetime import date, datetime, time, timedelta, timezone

import serde
from serde.toml import from_toml, to_toml
from serde.yaml import from_yaml, to_yaml


@serde.serde
class Memorial:
    """The day WW2 ends in Japanese time."""

    local_date: date = date(1945, 8, 15)
    local_time: time = time(12, 0, 0)
    local_datetime: datetime = datetime(1945, 8, 15, 12, 0, 0)
    offset_datetime: datetime = datetime(
        1945, 8, 15, 12, 0, 0, tzinfo=timezone(timedelta(seconds=32400))
    )


def test_datetime_toml() -> None:
    """
    Toml has various date time types: Offset Date-Time, Local Date-Time,
    Local Date, and Local Time.
    All these types are supported to convert datetime classes by tomli.
    """
    memorial = Memorial()
    expected = """local_date = 1945-08-15
local_time = 12:00:00
local_datetime = 1945-08-15 12:00:00
offset_datetime = 1945-08-15 12:00:00+09:00
"""
    rendered = to_toml(memorial)
    assert expected == rendered
    assert memorial == from_toml(Memorial, expected)


def test_datetime_yaml() -> None:
    """
    Yaml supports date, datetime, and datetime with offset, but it
    doesn't support local time.
    """
    memorial = Memorial()
    # Somehow pyyaml reorders keys alphabetically
    expected = """local_date: 1945-08-15
local_datetime: 1945-08-15 12:00:00
local_time: '12:00:00'
offset_datetime: 1945-08-15 12:00:00+09:00
"""
    rendered = to_yaml(memorial)
    assert expected == rendered
    assert memorial == from_yaml(Memorial, expected)
