#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dataclasses import dataclass
import serde
from serde.core import init

# Enable debug mode to see generated code
init(debug=True)


@serde.serde
@dataclass
class Small:
    i: int
    s: str
    f: float
    b: bool


# Create an instance and access the scope to see generated code
small = Small(i=10, s="hello", f=3.14, b=True)
scope = getattr(Small, serde.core.SERDE_SCOPE)
print("=== Generated Serialization Code ===")
for name, code in scope.code.items():
    print(f"\n--- {name} ---")
    print(code)

# Also show what functions are available
print("\n=== Available Functions ===")
for name, func in scope.funcs.items():
    print(f"{name}: {func}")
