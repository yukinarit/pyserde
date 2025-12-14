import sys
import typing


if sys.version_info[:3] < (3, 12, 0):
    print("examples require at least Python 3.12")
    sys.exit(1)


def run_all() -> None:
    import alias
    import any
    import class_var
    import primitive_subclass
    import collection
    import mapping
    import sequence
    import set_abc
    import custom_class_serializer
    import custom_legacy_class_serializer
    import custom_field_serializer
    import default
    import default_dict
    import env
    import flatten
    import forward_reference
    import frozen_set
    import generics
    import generics_pep695
    import generics_nested
    import nested
    import init_var
    import jsonfile
    import lazy_type_evaluation
    import literal
    import msg_pack
    import newtype
    import pep681
    import plain_dataclass
    import plain_dataclass_class_attribute
    import deny_unknown_fields
    import python_pickle
    import recursive
    import recursive_list
    import recursive_union
    import rename
    import rename_all
    import simple
    import skip
    import tomlfile
    import type_check_coerce
    import type_check_disabled
    import type_datetime
    import type_decimal
    import type_ipaddress
    import type_numpy
    import type_pathlib
    import type_uuid
    import type_alias_pep695
    import union
    import union_tagging
    import union_directly
    import user_exception
    import variable_length_tuple
    import type_statement
    import yamlfile
    import enum34
    import kw_only

    run(any)
    run(simple)
    run(enum34)
    run(frozen_set)
    run(newtype)
    run(collection)
    run(mapping)
    run(sequence)
    run(set_abc)
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
    run(custom_legacy_class_serializer)
    run(custom_field_serializer)
    run(forward_reference)
    run(type_decimal)
    run(type_datetime)
    run(union_tagging)
    run(union_directly)
    run(generics)
    run(type_alias_pep695)
    run(type_statement)
    run(generics_pep695)
    run(generics_nested)
    run(nested)
    run(lazy_type_evaluation)
    run(literal)
    run(type_check_coerce)
    run(type_check_disabled)
    run(user_exception)
    run(pep681)
    run(variable_length_tuple)
    run(init_var)
    run(python_pickle)
    run(class_var)
    run(alias)
    run(recursive)
    run(recursive_list)
    run(recursive_union)
    run(class_var)
    run(plain_dataclass)
    run(plain_dataclass_class_attribute)
    run(deny_unknown_fields)
    run(msg_pack)
    run(primitive_subclass)
    run(kw_only)
    run(type_pathlib)
    run(type_ipaddress)
    run(type_uuid)
    run(type_numpy)

    try:
        import type_sqlalchemy

        run(type_sqlalchemy)
    except ImportError:
        pass


def run(module: typing.Any) -> None:
    print("-----------------")
    print(f"running {module.__name__}")
    module.main()


if __name__ == "__main__":
    try:
        run_all()
        print("-----------------")
        print("all examples completed successfully!")
    except Exception:
        sys.exit(1)
