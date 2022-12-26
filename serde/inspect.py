"""
pyserde inspection tool.

#### Usage

```
$ python -m serde.inspect <PATH> <NAME>

 PATH  Python script path.
 NAME  Pyserde class name.
```

"""
import argparse
import importlib
import logging
import os
import sys

from typing_extensions import Type

from .core import SERDE_SCOPE, SerdeScope, init, logger

init(True)


def inspect(cls: Type) -> None:
    """
    Inspect a pyserde class.
    """
    scope: SerdeScope = getattr(cls, SERDE_SCOPE, {})
    print(scope)


def main(arg):
    """
    Main entrypoint of `serde.inspect`.
    """
    if arg.verbose:
        logging.basicConfig(level=logging.DEBUG)

    try:
        import black

        assert black
    except ImportError:
        logger.warning(('Tips: Installing "black" makes the output prettier! Try this command:\n' 'pip install back'))

    dir = os.path.dirname(arg.path)
    mod = os.path.basename(arg.path)[:-3]
    print(f'Loading {mod}.{arg.name} from {dir}/{mod}.py')
    sys.path.append(dir)
    pkg = importlib.import_module(mod)
    cls = getattr(pkg, arg.name)
    inspect(cls)


parser = argparse.ArgumentParser(description='pyserde-inspect')
parser.add_argument('path', type=str, help='Python script path.')
parser.add_argument('name', type=str, help='Pyserde class name.')
parser.add_argument('-v', dest='verbose', action='store_true', help='Enable debug logging.')


if __name__ == '__main__':
    args = parser.parse_args()
    main(args)
