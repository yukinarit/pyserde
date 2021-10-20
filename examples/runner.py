import sys

import any
import collection
import custom_class_serializer
import custom_field_serializer
import default
import env
import flatten
import forward_reference
import jsonfile
import newtype
import rename
import rename_all
import simple
import skip
import tomlfile
import type_datetime
import type_decimal
import union
import yamlfile

PY36 = sys.version_info[:3] < (3, 7, 0)

if not PY36:
    import lazy_type_evaluation


def run_all():
    run(any)
    run(simple)
    run(newtype)
    run(collection)
    run(default)
    run(env)
    run(flatten)
    run(jsonfile)
    run(rename)
    run(rename_all)
    run(skip)
    run(tomlfile)
    run(yamlfile)
    run(union)
    run(custom_class_serializer)
    run(custom_field_serializer)
    run(forward_reference)
    run(type_decimal)
    run(type_datetime)
    if not PY36:
        run(lazy_type_evaluation)


def run(module):
    print('-----------------')
    print(f'running {module.__name__}')
    module.main()


if __name__ == '__main__':
    try:
        run_all()
    except Exception:
        sys.exit(1)
