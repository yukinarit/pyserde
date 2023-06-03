import enum
from dataclasses import dataclass
from typing import Any, Callable


class Size(enum.Enum):
    Small = "Small"
    Medium = "Medium"
    Large = "Large"


@dataclass
class Runner:
    name: Size
    data: Any
    se: Callable
    de: Callable
    astuple: Callable
    asdict: Callable
