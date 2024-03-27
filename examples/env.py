from envclasses import envclass, load_env
from pathlib import Path

from serde import deserialize
from serde.yaml import from_yaml

basedir = Path(__file__).parent


@deserialize
@envclass
class App:
    addr: str
    port: int
    secret: str
    workers: int


def main() -> None:
    with open(basedir / "app.yml") as f:
        yml = f.read()
    cfg = from_yaml(App, yml)
    print(cfg)

    load_env(cfg, prefix="APP")
    print(cfg)


if __name__ == "__main__":
    main()
