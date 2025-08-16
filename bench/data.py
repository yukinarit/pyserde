import json
from typing import Any

SMALL = '{"i": 10, "s": "foo", "f": 100.0, "b": true}'

SMALL_TUPLE = (10, "foo", 100.0, True)

SMALL_DICT = json.loads(SMALL)

MEDIUM = f'{{"inner": [{",".join([SMALL] * 50)}]}}'

MEDIUM_TUPLE = ([[SMALL_TUPLE] * 50],)

json_md = (
    '{"i": 10, "s": "foo", "f": 100.0, "b": true,'
    '"i2": 10, "s2": "foo", "f2": 100.0, "b2": true,'
    '"i3": 10, "s3": "foo", "f3": 100.0, "b3": true,'
    '"i4": 10, "s4": "foo", "f4": 100.0, "b4": true,'
    '"i5": 10, "s5": "foo", "f5": 100.0, "b5": true}'
)

json_pri_container = (
    '{"v": [1, 2, 3, 4, 5], "d": {"foo": 10, "fuga": 20}, "foo": 30, "t": [true, false, true]}'
)

args_sm = {"i": 10, "s": "foo", "f": 100.0, "b": True}

args_md = [args_sm] * 50

# Large test data with lists, dicts, nested structures and unions
json_large_nested = (
    '{"customer_id": 12345, "name": "John Smith", "email": "john@example.com", '
    '"address": {"street": "123 Main St", "city": "New York", '
    '"country": "USA", "postal_code": "10001"}, '
    '"orders": [{"order_id": "ORD-001", "items": [{"product_id": 1, "name": "Laptop", '
    '"price": 999.99, "quantity": 1, "tags": ["electronics", "computer"]}, '
    '{"product_id": 2, "name": "Mouse", "price": 29.99, "quantity": 2, '
    '"tags": ["electronics", "accessory"]}], '
    '"total": 1059.97, "status": "shipped", '
    '"metadata": {"priority": "high", "notes": "Express delivery"}}, '
    '{"order_id": "ORD-002", "items": [{"product_id": 3, "name": "Book", '
    '"price": 19.99, "quantity": 3, "tags": ["books", "education"]}], '
    '"total": 59.97, "status": "processing", "metadata": {"priority": "normal", "notes": null}}], '
    '"preferences": {"theme": "dark", "notifications": true, '
    '"language": "en", "max_budget": 5000}, '
    '"loyalty_points": 1250, "created_at": "2024-01-15T10:30:00Z"}'
)

# Generate LARGE JSON data programmatically to avoid long lines


def _create_large_data() -> dict[str, Any]:
    items_list = ["laptop", "mouse", "keyboard", "monitor", "speakers"] * 20
    nested_data = {
        "category_1": list(range(50)),
        "category_2": list(range(50, 100)),
        "category_3": list(range(100, 150)),
        "category_4": list(range(150, 200)),
        "category_5": list(range(200, 250)),
    }

    return {
        "customer_id": 12345,
        "name": "John Smith",
        "email": "john@example.com",
        "preferences": {
            "theme": "dark",
            "notifications": True,
            "language": "en",
            "max_budget": 5000,
            "auto_renew": False,
            "privacy_level": 3,
        },
        "items_list": items_list,
        "nested_data": nested_data,
        "loyalty_points": 1250,
        "created_at": "2024-01-15T10:30:00Z",
    }


LARGE = json.dumps(_create_large_data())

# Complex nested args for large data
args_large = {
    "customer_id": 12345,
    "name": "John Smith",
    "email": "john@example.com",
    "address": {
        "street": "123 Main St",
        "city": "New York",
        "country": "USA",
        "postal_code": "10001",
    },
    "orders": [
        {
            "order_id": "ORD-001",
            "items": [
                {
                    "product_id": 1,
                    "name": "Laptop",
                    "price": 999.99,
                    "quantity": 1,
                    "tags": ["electronics", "computer"],
                },
                {
                    "product_id": 2,
                    "name": "Mouse",
                    "price": 29.99,
                    "quantity": 2,
                    "tags": ["electronics", "accessory"],
                },
            ],
            "total": 1059.97,
            "status": "shipped",
            "metadata": {"priority": "high", "notes": "Express delivery"},
        },
        {
            "order_id": "ORD-002",
            "items": [
                {
                    "product_id": 3,
                    "name": "Book",
                    "price": 19.99,
                    "quantity": 3,
                    "tags": ["books", "education"],
                }
            ],
            "total": 59.97,
            "status": "processing",
            "metadata": {"priority": "normal", "notes": None},
        },
    ],
    "preferences": {"theme": "dark", "notifications": True, "language": "en", "max_budget": 5000},
    "loyalty_points": 1250,
    "created_at": "2024-01-15T10:30:00Z",
}
