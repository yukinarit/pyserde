# API Reference

This page provides comprehensive API documentation for the pyserde library, automatically generated from source code docstrings.

::: serde
    options:
      members:
        - serde
        - serialize
        - deserialize
        - is_serializable
        - is_deserializable
        - to_dict
        - from_dict
        - to_tuple
        - from_tuple
        - SerdeError
        - SerdeSkip
        - AdjacentTagging
        - ExternalTagging
        - InternalTagging
        - Untagged
        - disabled
        - strict
        - coerce
        - field
        - default_deserializer
        - asdict
        - astuple
        - default_serializer
        - ClassSerializer
        - ClassDeserializer
        - add_serializer
        - add_deserializer

::: serde.json
    options:
      members:
        - from_json
        - to_json

::: serde.yaml
    options:
      members:
        - from_yaml
        - to_yaml

::: serde.toml
    options:
      members:
        - from_toml
        - to_toml

::: serde.msgpack
    options:
      members:
        - from_msgpack
        - to_msgpack

::: serde.pickle
    options:
      members:
        - from_pickle
        - to_pickle
