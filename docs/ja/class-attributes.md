# クラスアトリビュート

クラスアトリビュートは`@serde`, `@serialize`, `@deserialize`デコレートに指定できるアトリビュートで、クラス全体の振る舞いをカスタマイズすることができます。

## **`rename_all`**

`rename_all`を使うとクラス全体のフィールド名のcaseを変換することができます。
例えば以下のコードは`snake_case`のフィールドを`camelCase`に変換します。使用可能なstring caseは[こちら](https://dmlls.github.io/python-casefy/api.html)参照のこと。もし、`rename_all`と後述の`rename`フィールドアトリビュートが指定された場合は、`rename`が優先されます。

```python
@serde(rename_all = 'camelcase')
@dataclass
class Foo:
    int_field: int
    str_field: str

f = Foo(int_field=10, str_field='foo')
print(to_json(f))
```

出力結果のフィールド名は全て`camelCase`になりました。

```json
{"intField": 10, "strField": "foo"}
```

examplesの[rename_all.py](https://github.com/yukinarit/pyserde/blob/main/examples/rename_all.py)も参考にしてみてください。

## **`tagging`**

## **`serializer`**

## **`type_check`**

## **`serialize_class_var`**
