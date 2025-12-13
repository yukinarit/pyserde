# type: ignore  # SQLAlchemy types imported via pytest.importorskip
import logging
from typing import Any

import pytest

import serde
from .common import (
    opt_case,
    opt_case_ids,
    FormatFuncs,
    format_dict,
    format_tuple,
    format_json,
    format_msgpack,
    format_yaml,
    format_pickle,
    format_toml,
    all_formats,
)

sa = pytest.importorskip("sqlalchemy", "2.0.0")
sa_orm = pytest.importorskip("sqlalchemy.orm")

log = logging.getLogger("test")

serde.init(True)

all_except_toml: FormatFuncs = (
    format_dict + format_tuple + format_json + format_msgpack + format_yaml + format_pickle
)


@pytest.mark.parametrize("opt", opt_case, ids=opt_case_ids())
@pytest.mark.parametrize("se,de", all_except_toml)
def test_sqlalchemy_simple(se: Any, de: Any, opt: Any) -> None:
    log.info(f"Running test with se={se.__name__} de={de.__name__} opts={opt}")

    class Base(sa_orm.MappedAsDataclass, sa_orm.DeclarativeBase):
        pass

    @serde.serde(**opt)
    class User(Base):
        __tablename__ = "user"

        id: sa_orm.Mapped[int] = sa_orm.mapped_column(primary_key=True)
        name: sa_orm.Mapped[str]
        fullname: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(30))
        nickname: sa_orm.Mapped[str | None] = sa_orm.mapped_column(init=False)

    user = User(1, "john", "John Doe")
    assert user == de(User, se(user))


@pytest.mark.parametrize("opt", opt_case, ids=opt_case_ids())
@pytest.mark.parametrize("se,de", format_toml)
def test_sqlalchemy_simple_toml(se: Any, de: Any, opt: Any) -> None:
    log.info(f"Running test with se={se.__name__} de={de.__name__} opts={opt}")

    class Base(sa_orm.MappedAsDataclass, sa_orm.DeclarativeBase):
        pass

    @serde.serde(**opt)
    class User(Base):
        __tablename__ = "user"

        id: sa_orm.Mapped[int] = sa_orm.mapped_column(primary_key=True)
        name: sa_orm.Mapped[str]
        fullname: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(30))

    user = User(1, "john", "John Doe")
    assert user == de(User, se(user))


@pytest.mark.parametrize("opt", opt_case, ids=opt_case_ids())
@pytest.mark.parametrize("se,de", all_formats)
def test_sqlalchemy_nested(se: Any, de: Any, opt: Any) -> None:
    log.info(f"Running test with se={se.__name__} de={de.__name__} opts={opt}")

    class Base(sa_orm.MappedAsDataclass, sa_orm.DeclarativeBase):
        pass

    @serde.serde(**opt)
    class Project(Base):
        __tablename__ = "projects"
        id: sa_orm.Mapped[int] = sa_orm.mapped_column(primary_key=True)
        name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False)
        owner_id: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.ForeignKey("users.id"))

    @serde.serde(**opt)
    class User(Base):
        __tablename__ = "users"

        id: sa_orm.Mapped[int] = sa_orm.mapped_column(primary_key=True)
        name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False)
        fullname: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False)
        projects: sa_orm.Mapped[list[Project]] = sa_orm.relationship(backref="owner")

    user = User(1, "john", "John Doe", [Project(1, "Dummy", 1)])
    assert user == de(User, se(user))
