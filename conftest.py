# see https://docs.pytest.org/en/latest/example/pythoncollection.html#customizing-test-collection
import sys

collect_ignore = ["setup.py"]

if sys.version_info[:2] == (3, 6):
    # skip these tests for python 3.6 because it does not support PEP 563
    collect_ignore.append("tests/test_lazy_type_evaluation.py")
