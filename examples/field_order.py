from serde import serde, field


@serde
class Foo:
    id: int = field(rename="ID")  # Field with attributes can be defined before other fields
    # thanks to dataclass_transform field_specifiers
    # https://peps.python.org/pep-0681/#the-dataclass-transform-decorator
    # NOTE: you still get error with mypy as of mypy v1.8.0
    comments: str


if __name__ == "__main__":
    pass
