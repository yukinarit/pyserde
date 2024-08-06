# Extending pyserde

pyserde はビルトイン型以外をサポートするために pyserde を拡張する 3 つの方法を提供しています。

## カスタムフィールド（デ）シリアライザ

詳細は[カスタムフィールドシリアライザ](./field-attributes.md#serializerdeserializer)を参照してください。

> 💡 ヒント：`serde.field` を独自のフィールド関数でラップすると以下のようになります。
>
> ```python
> import serde
>
> def field(*args, **kwargs):
>     serde.field(*args, **kwargs, serializer=str)
>
> @serde
> class Foo:
>     a: int = field(default=0)  # フィールドシリアライザの設定
> ```

## カスタムクラス（デ）シリアライザ

詳細は[カスタムクラスシリアライザ](./class-attributes.md#class_serializer--class_deserializer)を参照してください。

## カスタムグローバル（デ）シリアライザ

`add_serializer` と `add_deserializer` を使ってクラス（デ）シリアライザを登録することで、コードベース全体でカスタム（デ）シリアライザを適用できます。

登録されたクラス（デ）シリアライザは pyserde のグローバル空間にスタックされ、すべての pyserde クラスで自動的に使用されます。

例：[isodate](https://pypi.org/project/isodate/)パッケージを使用して `datetime.timedelta` のカスタム（デ）シリアライザを実装する。

以下は、`datetime.timedelta` のためのクラス（デ）シリアライザを登録するコードです。  
このパッケージは実際に PyPI で [pyserde-timedelta](https://pypi.org/project/pyserde-timedelta/) として公開されています。

```python
from datetime import timedelta
from plum import dispatch
from typing import Type, Any
import isodate
import serde

class Serializer:
    @dispatch
    def serialize(self, value: timedelta) -> Any:
        return isodate.duration_isoformat(value)

class Deserializer:
    @dispatch
    def deserialize(self, cls: Type[timedelta], value: Any) -> timedelta:
        return isodate.parse_duration(value)

def init() -> None:
    serde.add_serializer(Serializer())
    serde.add_deserializer(Deserializer())
```

このパッケージの利用者は、 `serde_timedelta.init()` を呼び出すだけで `datetime.timedelta` のカスタム（デ）シリアライザの機能を再利用できます。

```python
import serde_timedelta
from serde import serde
from serde.json import to_json, from_json
from datetime import timedelta

serde_timedelta.init()

@serde
class Foo:
    a: timedelta

f = Foo(timedelta(hours=10))
json = to_json(f)
print(json)
print(from_json(Foo, json))
```

以下のように `datetime.timedelta` がISO 8601 形式でシリアライズされます！

```bash
{"a":"PT10H"}
Foo(a=datetime.timedelta(seconds=36000))
```

> 💡 ヒント：クラス（デ）シリアライザはいくつでも登録できます。これは、好きなだけpyserde拡張を使用できることを意味します。
> 登録された（デ）シリアライザはメモリにスタックされます。
>
> なお、1つの（デ）シリアライザは他の（デ）シリアライザによってオーバーライドされる可能性があります。
>
> 例：次の順序で3つのカスタムシリアライザを登録すると、最初のシリアライザは3番目によって完全に上書きされます。2番目は異なる型用に実装されているため機能します。
>
> 1. `int` 用のシリアライザを登録
> 2. `float` 用のシリアライザを登録
> 3. `int` 用のシリアライザを登録

こちらは、v0.13.0 で新しく追加されました。
