import enum
from dataclasses import dataclass
from collections.abc import Callable
from typing import Any, Optional


class Size(enum.Enum):
    Small = "Small"
    Medium = "Medium"
    Large = "Large"


@dataclass
class Runner:
    name: str
    data: Any
    se: Optional[Callable[..., Any]]
    de: Optional[Callable[..., Any]]
    astuple: Optional[Callable[..., Any]]
    asdict: Optional[Callable[..., Any]]
