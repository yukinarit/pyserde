import sys

import basics
import default
import env
import jsonfile
import rename
import skip
import tomlfile
import yamlfile


def run_all():
    run(basics)
    run(default)
    run(env)
    run(rename)
    run(skip)
    run(jsonfile)
    run(tomlfile)
    run(yamlfile)


def run(module):
    print(f'running {module.__name__}')
    module.main()


if __name__ == '__main__':
    try:
        run_all()
    except Exception:
        sys.exit(1)
