from functools import partial
from typing import Any, Union

import data
from pydantic import BaseModel
from runner import Runner, Size


class Small(BaseModel):
    i: int
    s: str
    f: float
    b: bool


class Medium(BaseModel):
    inner: list[Small] = []


class Large(BaseModel):
    customer_id: int
    name: str
    email: str
    preferences: dict[str, Union[str, bool, int]] = {}
    items_list: list[str] = []
    nested_data: dict[str, list[int]] = {}
    loyalty_points: int = 0
    created_at: str = ""


SMALL = Small(**data.args_sm)

MEDIUM = Medium(inner=[Small(**d) for d in data.args_md])


# Create Large instance with simpler structure but complex data
def create_large_instance() -> Large:
    return Large(
        customer_id=12345,
        name="John Smith",
        email="john@example.com",
        preferences={
            "theme": "dark",
            "notifications": True,
            "language": "en",
            "max_budget": 5000,
            "auto_renew": False,
            "privacy_level": 3,
        },
        items_list=["laptop", "mouse", "keyboard", "monitor", "speakers"] * 20,  # 100 items
        nested_data={
            "category_1": list(range(50)),
            "category_2": list(range(50, 100)),
            "category_3": list(range(100, 150)),
            "category_4": list(range(150, 200)),
            "category_5": list(range(200, 250)),
        },
        loyalty_points=1250,
        created_at="2024-01-15T10:30:00Z",
    )


LARGE = create_large_instance()


def new(size: Size) -> Runner:
    name = "pydantic"
    if size == Size.Small:
        unp = SMALL
        pac = data.SMALL
        cls = Small
    elif size == Size.Medium:
        unp = MEDIUM  # type: ignore[assignment]
        pac = data.MEDIUM
        cls = Medium  # type: ignore[assignment]
    elif size == Size.Large:
        unp = LARGE  # type: ignore[assignment]
        pac = data.LARGE
        cls = Large  # type: ignore[assignment]
    return Runner(name, unp, partial(se, unp), partial(de, cls, pac), None, partial(asdict, unp))


def se(obj: Union[Small, Medium, Large]) -> str:
    return obj.model_dump_json()


def de(
    cls: Union[type[Small], type[Medium], type[Large]], data: str
) -> Union[Small, Medium, Large]:
    return cls.model_validate_json(data)


def asdict(obj: Union[Small, Medium, Large]) -> dict[str, Any]:
    return obj.model_dump()
