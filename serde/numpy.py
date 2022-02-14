from typing import Any, Callable, Optional

from serde.compat import get_args, get_origin


def fullname(klass):
    module = klass.__module__
    if module == 'builtins':
        return klass.__qualname__  # avoid outputs like 'builtins.str'
    return module + '.' + klass.__qualname__


def is_numpy_type(typ) -> bool:
    return is_bare_numpy_array(typ) or is_numpy_scalar(typ) or is_numpy_array(typ)


def is_numpy_available() -> bool:
    return encode_numpy is not None


try:
    import numpy as np
    import numpy.typing as npt

    encode_numpy: Optional[Callable[[Any], Any]]

    def encode_numpy(obj: Any):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.datetime64):
            return obj.item().isoformat()
        if isinstance(obj, np.generic):
            return obj.item()
        raise TypeError(f"Object of type {fullname(type(obj))} is not serializable")

    def is_bare_numpy_array(typ) -> bool:
        """
        Test if the type is `np.ndarray` or `npt.NDArray` without type args.

        >>> import numpy as np
        >>> import numpy.typing as npt
        >>> is_bare_numpy_array(npt.NDArray[np.int64])
        False
        >>> is_bare_numpy_array(npt.NDArray)
        True
        >>> is_bare_numpy_array(np.ndarray)
        True
        """
        return typ in (np.ndarray, npt.NDArray)

    def is_numpy_scalar(typ) -> bool:
        try:
            return issubclass(typ, np.generic)
        except TypeError:
            return False

    def is_numpy_datetime(typ) -> bool:
        try:
            return issubclass(typ, np.datetime64)
        except TypeError:
            return False

    def serialize_numpy_scalar(arg) -> str:
        return f"{arg.varname}.item()"

    def deserialize_numpy_scalar(arg):
        return f"{fullname(arg.type)}({arg.data})"

    def is_numpy_array(typ) -> bool:
        origin = get_origin(typ)
        if origin is not None:
            typ = origin
        return typ is np.ndarray

    def serialize_numpy_array(arg) -> str:
        return f"{arg.varname}.tolist()"

    def serialize_numpy_datetime(arg) -> str:
        return f"{arg.varname}.item().isoformat()"

    def deserialize_numpy_array(arg) -> str:
        if is_bare_numpy_array(arg.type):
            return f"numpy.array({arg.data})"

        dtype = fullname(arg[1][0].type)
        return f"numpy.array({arg.data}, dtype={dtype})"

    def deserialize_numpy_array_direct(typ, arg):
        if is_bare_numpy_array(typ):
            return np.array(arg)

        dtype = get_args(get_args(typ)[1])[0]
        return np.array(arg, dtype=dtype)

except ImportError:
    encode_numpy = None

    def is_numpy_scalar(typ) -> bool:
        return False

    def is_numpy_datetime(typ) -> bool:
        return False

    def serialize_numpy_scalar(arg) -> str:
        return ""

    def deserialize_numpy_scalar(arg):
        return ""

    def is_numpy_array(typ) -> bool:
        return False

    def serialize_numpy_array(arg) -> str:
        return ""

    def serialize_numpy_datetime(arg) -> str:
        return ""

    def deserialize_numpy_array(arg) -> str:
        return ""

    def deserialize_numpy_array_direct(typ, arg):
        return arg
