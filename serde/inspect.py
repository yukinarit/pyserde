"""
pyserde inspect tool.

USAGE:

$ python -m serde.inspect <PATH> <NAME>

 PATH  Python script path.
 NAME  Pyserde class name.

"""
import argparse
import importlib
import os
import sys
from typing import Type

from .core import HIDDEN_NAME, init

init(True)


def inspect(cls: Type) -> str:
    """
    Inspect a pyserde class.
    """
    hidden = getattr(cls, HIDDEN_NAME, None)
    return '\n'.join(hidden.code.values())


def main(arg):
    dir = os.path.dirname(arg.path)
    mod = os.path.basename(arg.path)[:-3]
    print(f'Loading {mod}.{arg.name} from {dir}.')
    sys.path.append(dir)
    pkg = importlib.import_module(mod)
    cls = getattr(pkg, arg.name)
    print(inspect(cls))


parser = argparse.ArgumentParser(description='pyserde-inspect')
parser.add_argument('path', type=str, help='Python script path.')
parser.add_argument('name', type=str, help='Pyserde class name.')


if __name__ == '__main__':
    args = parser.parse_args()
    main(args)
