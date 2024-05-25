from typing import Any

try:
    from sqlalchemy.inspection import inspect
    from sqlalchemy.exc import NoInspectionAvailable

    def is_sqlalchemy_inspectable(subject: Any) -> bool:
        try:
            inspect(subject)
            return True
        except NoInspectionAvailable:
            return False

except ImportError:

    def is_sqlalchemy_inspectable(subject: Any) -> bool:
        return False
