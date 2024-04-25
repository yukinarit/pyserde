import logging
from typing import Optional

import pytest
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

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
)

log = logging.getLogger("test")

serde.init(True)

all_except_toml: FormatFuncs = (
    format_dict + format_tuple + format_json + format_msgpack + format_yaml + format_pickle
)


@pytest.mark.parametrize("opt", opt_case, ids=opt_case_ids())
@pytest.mark.parametrize("se,de", all_except_toml)
def test_sqlalchemy_simple(se, de, opt):
    log.info(f"Running test with se={se.__name__} de={de.__name__} opts={opt}")

    class Base(MappedAsDataclass, DeclarativeBase):
        pass

    @serde.serde(**opt)
    class User(Base):
        __tablename__ = "user"

        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str]
        fullname: Mapped[str] = mapped_column(String(30))
        nickname: Mapped[Optional[str]] = mapped_column(init=False)

    user = User(1, "john", "John Doe")
    assert user == de(User, se(user))


@pytest.mark.parametrize("opt", opt_case, ids=opt_case_ids())
@pytest.mark.parametrize("se,de", format_toml)
def test_sqlalchemy_simple_toml(se, de, opt):
    log.info(f"Running test with se={se.__name__} de={de.__name__} opts={opt}")

    class Base(MappedAsDataclass, DeclarativeBase):
        pass

    @serde.serde(**opt)
    class User(Base):
        __tablename__ = "user"

        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str]
        fullname: Mapped[str] = mapped_column(String(30))

    user = User(1, "john", "John Doe")
    assert user == de(User, se(user))
