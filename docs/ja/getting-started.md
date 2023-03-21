# 始めてみましょう

## インストール

まずはPyPIからpyserdeをインストールします。

```
pip install pyserde
```

Poetryの場合は以下のコマンドを使います。
```
poetry add pyserde
```

JSONとPickle以外のデータフォーマットを使う場合は、追加のパッケージインストールが必要になります。pyserdeでは`msgpack`, `toml`, `yaml`のextrasが用意されています。もし特定のデータフォーマットしか使用する予定がない場合、extrasを指定することによって余計なパッケージをインストールせずに済みます。例えばTomlとYAMLだけ使いたい場合は、

```
pip install "pyserde[toml,yaml]"
```

Poetryの場合は
```
poetry add pyserde -E toml -E yaml
```

全てのExtrasを指定したい場合は`all`を使えます。

```
pip install "pyserde[all]"
```

Poetryの場合は
```
poetry add pyserde -E all
```

## pyserdeを使ってクラスを定義する

次にpyserdeの`@serde`デコレータを使って以下のクラスを定義してみましょう。pyserdeのパッケージ名は`pyserde`ではなく、`serde`ですので間違えないようにしましょう。pyserdeは標準ライブラリの`dataclasses`モジュールに強く依存しています。もし`dataclasses`を一度も使ったことない場合は、 [dataclassesのドキュメンテーション](https://docs.python.org/ja/3/library/dataclasses.html)に目を通してみてください。

```python
from dataclasses import dataclass
from serde import serde

@serde
@dataclass
class Foo:
    i: int
    s: str
    f: float
    b: bool
```

pyserdeは`@serde`を付けたクラスがインタプリタにロードされる時と、そのクラスにシリアライズ・デシリアライズに必要なメソッドを自動的にコード生成します。コード生成はロード時に一度だけ行われるので、ランタイムでのオーバーヘッドはありません。これで定義したクラスが様々なデータフォーマットにシリアライズ・デシリアライズ可能になりました。

> **NOTE:** もしシリアライズかデシリアライズのどちらかしかしない場合は、`@serde`の代わりに`@serialize`と`@deserialize`デコレータを使うことができます。
>
> e.g. 例えばデシリアライズの機能を必要としない場合は、以下のように`@serrialize`デコレータだけ付けます。この場合、シリアライズのAPI (e.g. `to_json`)は使えますが、デシリアライズAPI(e.g. `from_json`)を呼び出すとエラーになります。 

> ```python
> from dataclasses import dataclass
> from serde import serialize
>
> @serialize
> @dataclass
> class Foo:
>     i: int
>     s: str
>     f: float
>     b: bool
> ```

## クラスを使ってみる

次にpyserdeのシリアライズ・デシリアライズAPIをインポートします。JSONの場合は、
Next, import pyserde (de)serialize API. For JSON:

```python
from serde.json import from_json, to_json
```

同様に他のデータフォーマットでは以下のようにimportします。
```python
from serde.yaml import from_yaml, to_yaml
from serde.toml import from_toml, to_toml
from serde.msgpack import from_msgpack to_msgpack
```

`to_json`でオブジェクトをシリアライズしてみます。
```
f = Foo(i=10, s='foo', f=100.0, b=True)
print(to_json(f))
```

今度は`from_json`に`Foo`とJSONを渡してJSONから`Foo`のオブジェクトにデシリアライズしてみます。
```python
s = '{"i": 10, "s": "foo", "f": 100.0, "b": true}'
print(from_json(Foo, s))
```

シリアライズ・デシリアライズできました！pyserdeはこの他にもたくさんの機能があるので興味がある人はドキュメントを読み進めてみてください。
