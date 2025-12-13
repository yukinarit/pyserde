from sqlalchemy import Text, JSON, ForeignKey
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, Mapped, mapped_column, relationship

from serde import serde
from serde.json import from_json, to_json


class Base(MappedAsDataclass, DeclarativeBase):  # type: ignore[misc]
    pass


@serde
class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))


@serde
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    fullname: Mapped[str] = mapped_column(Text, nullable=False)
    nickname: Mapped[str | None] = mapped_column(Text)
    attributes: Mapped[dict[str, str] | None] = mapped_column(JSON)
    projects: Mapped[list[Project]] = relationship(backref="owner")


def main() -> None:
    user = User(
        id=1,
        name="john",
        fullname="John Doe",
        nickname=None,
        attributes={"color": "green"},
        projects=[Project(id=1, name="Dummy", owner_id=1)],
    )
    print(f"Into Json: {to_json(user)}")

    s = """{
        "id": 1,
        "name": "john",
        "fullname": "John Doe",
        "nickname": null,
        "attributes": {
            "color": "green"
        },
        "projects": [
            {
                "id": 1,
                "name": "Dummy",
                "owner_id": 1
            }
        ]
    }"""
    print(f"From Json: {from_json(User, s)}")


if __name__ == "__main__":
    main()
