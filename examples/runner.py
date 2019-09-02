import sys

import env
import jsonfile
import rename
import skip
import tomlfile
import yamlfile


def run_all():
    run(env)
    run(jsonfile)
    run(rename)
    run(skip)
    run(tomlfile)
    run(yamlfile)


def run(module):
    print(f'running {module.__name__}')
    module.main()


if __name__ == '__main__':
    try:
        run_all()
    except:
        sys.exit(1)
