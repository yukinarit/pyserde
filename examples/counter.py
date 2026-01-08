from collections import Counter

from serde import serde
from serde.json import from_json, to_json


@serde
class WordCount:
    counts: Counter[str]


def main() -> None:
    # Create a Counter from a list of words
    wc = WordCount(counts=Counter(["apple", "banana", "apple", "cherry", "banana", "apple"]))
    print(f"Original: {wc}")
    print(f"Into Json: {to_json(wc)}")

    # Deserialize from JSON
    s = '{"counts": {"apple": 3, "banana": 2, "cherry": 1}}'
    print(f"From Json: {from_json(WordCount, s)}")

    # Counter methods still work after deserialization
    wc2 = from_json(WordCount, s)
    print(f"Most common: {wc2.counts.most_common(2)}")


if __name__ == "__main__":
    main()
