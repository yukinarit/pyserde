# Class Attributes

クラス属性は、クラスの（デ）シリアライズの動作をカスタマイズするために `serialize` / `deserialize` デコレータの引数として指定できます。  
フィールドをカスタマイズしたい場合は、[フィールド属性](field-attributes.md)の使用を検討してください。

クラス属性は全フィールドに影響するため、命名規則やタグ付けなどクラス全体に共通する挙動に向いています。

## dataclassesの属性

### **`frozen`**

dataclassの `frozen` クラス属性は期待通りに機能します。

### **`kw_only`**

バージョン0.12.2で新規追加。dataclassの `kw_only` クラス属性は期待通りに機能します。

```python
@serde
@dataclass(kw_only=True)
class Foo:
    i: int
    s: str
    f: float
    b: bool
```

完全な例については、[examples/kw_only.py](https://github.com/yukinarit/pyserde/blob/main/examples/kw_only.py)を参照してください。

## pyserdeの属性

### **`rename_all`**

`rename_all` を使うと、フィールド名を指定されたケーススタイルに変換できます。  
以下の例では、キャメルケースのフィールド名をスネークケースに変換しています。
ケーススタイルの変換処理は [python-casefy](https://github.com/dmlls/python-casefy) パッケージに依存しています。  
サポートされるケーススタイルの一覧は [python-casefy のドキュメント](https://dmlls.github.io/python-casefy/api.html)を参照してください。

```python
@serde(rename_all = 'camelcase')
class Foo:
    int_field: int
    str_field: str

f = Foo(int_field=10, str_field='foo')
print(to_json(f))
```

上記のコードを実行すると、`int_field` は `intField` に、`str_field` は `strField` に変換されます。

```json
{"intField": 10, "strField": "foo"}
```

!!! note
    `rename_all` クラス属性と `rename` フィールド属性が同時に使用される場合、`rename` が優先されます。

    ```python
    @serde(rename_all = 'camelcase')
    class Foo:
        int_field: int
        str_field: str = field(rename='str-field')

    f = Foo(int_field=10, str_field='foo')
    print(to_json(f))
    ```
    上記のコードは以下を出力します。
    ```
    {"intField": 10, "str-field": "foo"}
    ```

完全な例については、[examples/rename_all.py](https://github.com/yukinarit/pyserde/blob/main/examples/rename_all.py)を参照してください。

### **`tagging`**

バージョン0.7.0で新規追加。詳細は [Union](union.md) を参照してください。

### **`transparent`**

`transparent=True` を指定すると、単一フィールドのラッパークラスはそのフィールドとして(デ)シリアライズされます（serde-rs の `#[serde(transparent)]` と同様）。

```python
@serde(transparent=True)
class UserId:
    value: int

assert to_json(UserId(1)) == "1"
assert from_json(UserId, "1") == UserId(1)
```

制約:
* `init=True` かつ `skip=False` のフィールドがちょうど1つ必要です。
* それ以外のフィールドは `init=False` かつ `skip=True` である必要があります（内部キャッシュ用途など）。

### **`class_serializer`** と **`class_deserializer`**

バージョン0.13.0で新規追加。  

クラスレベルでカスタム(デ)シリアライザを使用したい場合、`class_serializer` および `class_deserializer` 属性に(デ)シリアライザオブジェクトを渡すことができます。  
カスタム(デ)シリアライザは、C++のように複数のメソッドのオーバーロードを可能にするPythonライブラリ [plum](https://github.com/beartype/plum) に依存しています。  
plumを使用すると、堅牢なカスタム(デ)シリアライザを簡単に書くことができます。

```python
class MySerializer:
    @dispatch
    def serialize(self, value: datetime) -> str:
        return value.strftime("%d/%m/%y")

class MyDeserializer:
    @dispatch
    def deserialize(self, cls: Type[datetime], value:

 Any) -> datetime:
        return datetime.strptime(value, "%d/%m/%y")

@serde(class_serializer=MySerializer(), class_deserializer=MyDeserializer())
class Foo:
    v: datetime
```

旧来の `serializer` と `deserializer` との大きな違いは、 新しい`class_serializer` と `class_deserializer` が pyserde のコード生成レベルでより深く統合されていることです。  
これにより Optional や List、ネストされた dataclass を自分で処理する必要はありません。  

カスタムクラスの(デ)シリアライザはすべての(デ)シリアライズのレベル（単純なデータ型から複雑なネストされたデータ構造まで、あらゆる種類の(デ)シリアライズ処理）で使用されるため、サードパーティ製の型もビルトイン型のように扱うことが可能です。

また、
* フィールドシリアライザとクラスシリアライザの両方が指定されている場合、フィールドシリアライザが優先されます。
* 旧と新のクラスシリアライザの両方が指定されている場合、新しいクラスシリアライザが優先されます。

!!! tip
    複数の `serialize` メソッドを実装する場合、型チェッカーから、`Redefinition of unused serialize`という警告が出ることがあります。
    その場合は、`plum.overload` と `plum.dispatch` を使用して回避してください。
    詳細は [plumのドキュメント](https://beartype.github.io/plum/integration.html) を参照してください。

    ```python
    from plum import dispatch, overload

    class Serializer:
       # @overload を使用
       @overload
       def serialize(self, value: int) -> Any:
           return str(value)

       # @overload を使用
       @overload
       def serialize(self, value: float) -> Any:
           return int(value)

       # メソッド追加時は必ず @dispatch を追加してください。Plumが型チェッカーからの警告を消してくれます
       @dispatch
       def serialize(self, value: Any) -> Any:
           ...
    ```

完全な例については、[examples/custom_class_serializer.py](https://github.com/yukinarit/pyserde/blob/main/examples/custom_class_serializer.py)を参照してください。


### **`serializer`** と **`deserializer`**

!!! warning "非推奨"
    `serializer` と `deserializer` は、バージョン0.13.0以降、非推奨となりました。
    `class_serializer` および `class_deserializer` の使用を検討してください。

クラスレベルでカスタムの(デ)シリアライザを使用したい場合、`serializer` および `deserializer` 属性に(デ)シリアライザメソッドを渡すことができます。

```python
def serializer(cls, o):
    if cls is datetime:
        return o.strftime('%d/%m/%y')
    else:
        raise SerdeSkip()

def deserializer(cls, o):
    if cls is datetime:
        return datetime.strptime(o, '%d/%m/%y')
    else:
        raise SerdeSkip()

@serde(serializer=serializer, deserializer=deserializer)
class Foo:
    a: datetime
```

完全な例については、[examples/custom_legacy_class_serializer.py](https://github.com/yukinarit/pyserde/blob/main/examples/custom_legacy_class_serializer.py) を参照してください。

### **`type_check`**

バージョン0.9.0で新規追加。詳細は [Type Check](type-check.md) を参照してください。

### **`serialize_class_var`**

バージョン0.9.8で新規追加。  

`dataclasses.fields` はクラス変数を含まないため[^1]、pyserdeはデフォルトでクラス変数をシリアライズしません。  
`serialize_class_var` を使用することで `typing.ClassVar` のフィールドをシリアライズすることができます。

```python
@serde(serialize_class_var=True)
class Foo:
    a: ClassVar[int] = 10
```

完全な例については、[examples/class_var.py](https://github.com/yukinarit/pyserde/blob/main/examples/class_var.py)を参照してください。

[^1]: [dataclasses.fields](https://docs.python.org/3/library/dataclasses.html#dataclasses.fields)

### **`skip_if_default`**

バージョン0.30.0で新規追加。クラスデコレータに `skip_if_default=True` を指定すると、そのクラス内の全フィールドについて値がデフォルト（または `default_factory` の結果）と等しい場合に（デ）シリアライズをスキップします。フィールド側で `skip_if_default` を指定すればそちらが優先され、特定のフィールドだけ残す/外すことができます。

```python
@serde(skip_if_default=True)
class Settings:
    theme: str = "light"
    retries: int = 3
    api_key: str | None = None
    note: str = field(default="keep", skip_if_default=False)  # このフィールドは保持する
```

ネストしたdataclassや `default_factory` を使ったデフォルトも対象になります。動作例は [examples/skip_if_default_class.py](https://github.com/yukinarit/pyserde/blob/main/examples/skip_if_default_class.py) を参照してください。

### **`skip_if_none`**

バージョン0.30.0で新規追加。クラスデコレータに `skip_if_none=True` を指定すると、そのクラス内のフィールドが `None` の場合に（デ）シリアライズをスキップします。フィールド側で `skip_if_none` を指定すればそちらが優先されるため、特定のフィールドだけ残す/外すこともできます。

```python
@serde(skip_if_none=True)
class Profile:
    nickname: str | None = None
    bio: str | None = field(default=None, skip_if_none=False)  # None でも残す
```

`None` を大量に含むペイロードをコンパクトにしたい場合に便利です。

### **`deny_unknown_fields`**

バージョン0.22.0で新規追加。 pyserdeデコレータの`deny_unknown_fields`オプションはデシリアライズ時のより厳格なフィールドチェックを制御できます。このオプションをTrueにするとデシリアライズ時に宣言されていないフィールドが見つかると`SerdeError`を投げることができます。

以下の例を考えてください。
```python
@serde(deny_unknown_fields=True)
class Foo:
    a: int
    b: str
```

`deny_unknown_fields=True`が指定されていると、 宣言されているフィールド(この場合aとb)以外がインプットにあると例外を投げます。例えば、
```
from_json(Foo, '{"a": 10, "b": "foo", "c": 100.0, "d": true}')
```
上記のコードはフィールドcとdという宣言されていないフィールドがあるためエラーとなります。

完全な例については、[examples/deny_unknown_fields.py](https://github.com/yukinarit/pyserde/blob/main/examples/deny_unknown_fields.py)を参照してください。
