# Field Attributes

フィールド属性は、データクラスのフィールドの（デ）シリアライズ動作をカスタマイズするためのオプションです。

## dataclassesによって提供される属性

### **`default`** と **`default_factory`**

dataclassesの `default` と `default_factory` は期待通りに動作します。  
フィールドが `default` または `default_factory` 属性を持つ場合、そのフィールドはオプショナルフィールドのように振る舞います。  
フィールドがデータ内に存在する場合、当該フィールドの値がデシリアライズされたオブジェクトに設定されます。  
フィールドがデータ内に存在しない場合、指定されたデフォルト値がデシリアライズされたオブジェクトに設定されます。

```python
class Foo:
    a: int = 10
    b: int = field(default=10)  # field "a"と同じ
    c: dict[str, int] = field(default_factory=dict)

print(from_dict(Foo, {}))  # Foo(a=10, b=10, c={}) を出力
```

完全な例については、[examples/default.py](https://github.com/yukinarit/pyserde/blob/main/examples/default.py)を参照してください。

### **`ClassVar`**

`dataclasses.ClassVar` はデータクラスのクラス変数であり、dataclassはClassVarを擬似的なフィールドとして扱います。  
`dataclasses.field` はクラス変数を含まないため、pyserdeはデフォルトの動作として `ClassVar` フィールドを（デ）シリアライズしません。  
ClassVarフィールドをシリアライズする場合は、[serialize_class_var](class-attributes.md#serialize_class_var)クラス属性の使用を検討してください。

完全な例については、[examples/class_var.py](https://github.com/yukinarit/pyserde/blob/main/examples/class_var.py)を参照してください。

## pyserdeによって提供される属性

フィールド属性は `serde.field` または `dataclasses.field` を通じて指定することができます。  
型チェックが機能するため、 `serde.field` の使用を推奨します。

以下は、`rename` 属性を `serde.field` と `dataclasses.field` の両方で指定する例です。

```python
@serde.serde
class Foo:
    a: str = serde.field(rename="A")
    b: str = dataclasses.field(metadata={"serde_rename"="B"})
```

### **`rename`**

`rename` は（デ）シリアライズ中にフィールド名を変更するために使用されます。  
この属性は、フィールド名にPythonのキーワード（予約語）を使用したい場合に便利です。

以下のコードはフィールド名 `id` を `ID` に変更する例です。

```python
@serde
class Foo:
    id: int = field(rename="ID")
```

完全な例については、[examples/rename.py](https://github.com/yukinarit/pyserde/blob/main/examples/rename.py)を参照してください。

### **`skip`**

`skip` はこの属性を持つフィールドの（デ）シリアライズをスキップします。

```python
@serde
class Resource:
    name: str
    hash: str
    metadata: dict[str, str] = field(default_factory=dict, skip=True)
```

完全な例については、[examples/skip.py](https://github.com/yukinarit/pyserde/blob/main/examples/skip.py)を参照してください。

### **`skip_if`**

`skip_if` は条件関数が `True` を返す場合にフィールドの（デ）シリアライズをスキップします。

```python
@serde
class World:
    buddy: str = field(default='', skip_if=lambda v: v == 'Pikachu')
```

完全な例については、[examples/skip.py](https://github.com/yukinarit/pyserde/blob/main/examples/skip.py)を参照してください。

### **`skip_if_false`**

`skip_if_false` はフィールドが `False` と評価される場合にフィールドの（デ）シリアライズをスキップします。

例えば、以下のコードは `enemies` が空であれば（デ）シリアライズをスキップします。

```python
@serde
class World:
    enemies: list[str] = field(default_factory=list, skip_if_false=True)
```

完全な例については、[examples/skip.py](https://github.com/yukinarit/pyserde/blob/main/examples/skip.py)を参照してください。

### **`skip_if_default`**

`skip_if_default` はフィールドがデフォルト値とイコールである場合にフィールドの（デ）シリアライズをスキップします。

例えば、以下のコードは `town` が `Masara Town` であれば（デ）シリアライズをスキップします。

```python
@serde
class World:
    town: str = field(default='Masara Town', skip_if_default=True)
```

完全な例については、[examples/skip.py](https://github.com/yukinarit/pyserde/blob/main/examples/skip.py)を参照してください。

### **`alias`**

フィールド名に別名を設定できます。エイリアスはデシリアライズ時にのみ機能します。

```python
@serde
class Foo:
    a: str = field(alias=["b", "c"])
```

上記の例では、 `Foo` は `{"a": "..."}` , `{"b": "..."}` 、または `{"c": "..."}` のいずれかからデシリアライズできます。

完全な例については、[examples/alias.py](https://github.com/yukinarit/pyserde/blob/main/examples/alias.py)を参照してください。

## **`serializer`** と **`deserializer`**

特定のフィールドに対してカスタム（デ）シリアライザを使用したい場合があります。

例えば、以下のようなケースです。
* datetimeを異なる形式でシリアライズしたい。
* サードパーティパッケージの型をシリアライズしたい。

以下の例では、フィールド `a` はデフォルトのシリアライザで `"2021-01-01T00:00:00"` にシリアライズされますが、フィールド `b` はカスタムシリアライザで `"01/01/21"` にシリアライズされます。

```python
@serde
class Foo:
    a: datetime
    b: datetime = field(serializer=lambda x: x.strftime('%d/%m/%y'), deserializer=lambda x: datetime.strptime(x, '%d/%m/%y'))
```

完全な例については、[examples/custom_field_serializer.py](https://github.com/yukinarit/pyserde/blob/main/examples/custom_field_serializer.py)を参照してください。

## **`flatten`**

ネストされた構造のフィールドをフラットにできます。

```python
@serde
class Bar:
    c: float
    d: bool

@serde
class Foo:
    a: int
    b: str
    bar: Bar = field(flatten=True)
```

上記の例では、`Bar` の `c` および `d` フィールドが `Foo` で定義されているかのようにデシリアライズされます。  
`Foo` をJSON形式にシリアライズすると `{"a":10,"b":"foo","c":100.0,"d":true}` を取得します。

完全な例については、[examples/flatten.py](https://github.com/yukinarit/pyserde/blob/main/examples/flatten.py)を参照してください。
