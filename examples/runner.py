import sys

import alias
import any
import class_var
import collection
import custom_class_serializer
import custom_field_serializer
import default
import default_dict
import env
import flatten
import forward_reference
import frozen_set
import generics
import generics_nested
import init_var
import jsonfile
import lazy_type_evaluation
import literal
import msg_pack
import newtype
import pep681
import plain_dataclass
import plain_dataclass_class_attribute
import recursive
import recursive_list
import recursive_union
import rename
import rename_all
import simple
import skip
import tomlfile
import type_check_coerce
import type_check_strict
import type_datetime
import type_decimal
import union
import union_tagging
import user_exception
import variable_length_tuple
import yamlfile
import typing
import enum34

PY310 = sys.version_info[:3] >= (3, 10, 0)


def run_all() -> None:
    run(any)
    run(simple)
    run(enum34)
    run(frozen_set)
    run(newtype)
    run(collection)
    run(default)
    run(default_dict)
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
    run(union_tagging)
    run(generics)
    run(generics_nested)
    run(lazy_type_evaluation)
    run(literal)
    run(type_check_strict)
    run(type_check_coerce)
    run(user_exception)
    run(pep681)
    run(variable_length_tuple)
    run(init_var)
    run(class_var)
    run(alias)
    run(recursive)
    run(recursive_list)
    run(recursive_union)
    run(class_var)
    run(plain_dataclass)
    run(plain_dataclass_class_attribute)
    run(msg_pack)
    if PY310:
        import union_operator

        run(union_operator)


def run(module: typing.Any) -> None:
    print('-----------------')
    print(f'running {module.__name__}')
    module.main()


if __name__ == '__main__':
    try:
        run_all()
    except Exception:
        sys.exit(1)
