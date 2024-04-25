from typing import Any, Optional

try:
    from sqlalchemy.inspection import inspect
    from sqlalchemy.exc import NoInspectionAvailable

    def is_sqlalchemy_inspectable(subject: Any) -> bool:
        try:
            inspect(subject)
            return True
        except NoInspectionAvailable:
            return False

    def get_python_type(subject: Any) -> Any:
        if (obj := inspect(subject, raiseerr=False)) is None:
            return None
        return Optional[obj.type.python_type] if obj.nullable else obj.type.python_type

except ImportError:

    def is_sqlalchemy_inspectable(subject: Any) -> bool:
        return False

    def get_python_type(subject: Any) -> Any:
        return None
