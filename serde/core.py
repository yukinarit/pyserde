import logging
from typing import Dict, List, TypeVar

logger = logging.getLogger('serde')

JsonValue = TypeVar('JsonValue', str, int, float, bool, Dict, List)

T = TypeVar('T')

SE_NAME = '__serde_serialize__'

DE_NAME = '__serde_deserialize__'


class SerdeError(TypeError):
    """
    """


def gen(code: str, globals: Dict=None, locals: Dict=None, echo=False):
    """
    Customized exec function.
    """
    if echo:
        print(code)
    exec(code, globals, locals)
