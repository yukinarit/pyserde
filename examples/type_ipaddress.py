import ipaddress

from serde import serde
from serde.json import from_json, to_json


@serde
class Foo:
    v4: ipaddress.IPv4Address
    v6: ipaddress.IPv6Address
    v4n: ipaddress.IPv4Network
    v6n: ipaddress.IPv6Network


def main() -> None:
    foo = Foo(
        v4=ipaddress.IPv4Address("192.168.0.1"),
        v6=ipaddress.IPv6Address("2001:db8::"),
        v4n=ipaddress.IPv4Network("192.168.0.0/28"),
        v6n=ipaddress.IPv6Network("2001:db8::/32"),
    )
    print(f"Into Json: {to_json(foo)}")

    s = '{"v4": "192.168.0.1", "v6": "2001:db8::", "v4n": "192.168.0.0/28", "v6n": "2001:db8::/32"}'
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == "__main__":
    main()
