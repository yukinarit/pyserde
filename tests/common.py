from typing import List
from serde import from_dict, from_tuple, to_dict, to_tuple
from serde.json import from_json, to_json
from serde.msgpack import from_msgpack, to_msgpack
from serde.toml import from_toml, to_toml
from serde.yaml import from_yaml, to_yaml


format_dict: List = [(to_dict, from_dict)]

format_tuple: List = [(to_tuple, from_tuple)]

format_json: List = [(to_json, from_json)]

format_msgpack: List = [(to_msgpack, from_msgpack)]

format_yaml: List = [(to_yaml, from_yaml)]

format_toml: List = [(to_toml, from_toml)]

all_formats: List = format_dict + format_tuple + format_json + format_msgpack + format_yaml + format_toml
