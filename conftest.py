# see https://docs.pytest.org/en/latest/example/pythoncollection.html#customizing-test-collection
import sys

collect_ignore = ["setup.py"]

if sys.version_info[:2] < (3, 12):
    collect_ignore.append("tests/test_type_alias.py")
