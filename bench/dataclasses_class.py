import dataclasses
import json
from dataclasses import dataclass, field
from functools import partial
from typing import Any, Optional, Union

import data
from runner import Runner, Size


@dataclass
class Small:
    i: int
    s: str
    f: float
    b: bool


@dataclass
class Medium:
    inner: list[Small] = field(default_factory=list)


@dataclass
class Address:
    street: str
    city: str
    country: str
    postal_code: str


@dataclass
class Item:
    product_id: int
    name: str
    price: float
    quantity: int
    tags: list[str] = field(default_factory=list)


@dataclass
class Order:
    order_id: str
    items: list[Item] = field(default_factory=list)
    total: float = 0.0
    status: str = ""
    metadata: dict[str, Optional[str]] = field(default_factory=dict)


@dataclass
class Large:
    customer_id: int
    name: str
    email: str
    preferences: dict[str, Union[str, bool, int]] = field(default_factory=dict)
    items_list: list[str] = field(default_factory=list)
    nested_data: dict[str, list[int]] = field(default_factory=dict)
    loyalty_points: int = 0
    created_at: str = ""


SMALL = Small(**data.args_sm)

MEDIUM = Medium([Small(**d) for d in data.args_md])


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
    name = "dataclass"
    if size == Size.Small:
        unp = SMALL
    elif size == Size.Medium:
        unp = MEDIUM  # type: ignore[assignment]
    elif size == Size.Large:
        unp = LARGE  # type: ignore[assignment]
    return Runner(name, unp, partial(se, unp), None, partial(astuple, unp), partial(asdict, unp))


def se(obj: Union[Small, Medium, Large]) -> str:
    return json.dumps(asdict(obj))


def astuple(d: Union[Small, Medium, Large]) -> tuple[Any, ...]:
    return dataclasses.astuple(d)


def asdict(d: Union[Small, Medium, Large]) -> dict[str, Any]:
    return dataclasses.asdict(d)
