from dataclasses import dataclass

from envclasses import envclass, load_env

from serde import deserialize
from serde.yaml import from_yaml


@deserialize
@envclass
@dataclass
class App:
    addr: str
    port: int
    secret: str
    workers: int


def main():
    with open('app.yml') as f:
        yml = f.read()
    cfg = from_yaml(App, yml)
    print(cfg)

    load_env(cfg, prefix='APP')
    print(cfg)


if __name__ == '__main__':
    main()
