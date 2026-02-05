# Getting Started

## インストール

PyPIからpyserdeをインストールしてください。pyserdeにはPython>=3.10が必要です。

より高速なJSON処理が必要な場合は、`orjson` をインストールして `orjson` エクストラを利用できます。

```
pip install pyserde
```

uvを使用している場合は、以下のコマンドを実行してください。
```
uv add pyserde
```

JSONとPickle以外のデータ形式を扱う場合は、追加の依存関係をインストールする必要があります。  
適切なデータ形式で動作するには、`msgpack`、`toml`、`yaml` の追加パッケージをインストールしてください。  
使用しない場合はスキップして構いません。  
例えば、TomlとYAMLを使用する場合は以下のようにします。

```
pip install "pyserde[toml,yaml]"
```

uvを使用している場合
```
uv add pyserde --extra toml --extra yaml
```

一度にすべてをインストールする場合

```
pip install "pyserde[all]"
```

uvを使用している場合
```
uv add pyserde --extra all
```

利用可能な追加パッケージ:

* `all`：`msgpack`、`toml`、`yaml`、`numpy`、`orjson`、`sqlalchemy` をインストール
* `msgpack`：[msgpack](https://github.com/msgpack/msgpack-python) をインストール
* `toml`：[tomli](https://github.com/hukkin/tomli) と [tomli-w](https://github.com/hukkin/tomli-w) をインストール
* `yaml`：[pyyaml](https://github.com/yaml/pyyaml) をインストール
* `numpy`：[numpy](https://github.com/numpy/numpy) をインストール
* `orjson`：[orjson](https://github.com/ijl/orjson) をインストール
* `sqlalchemy`：[sqlalchemy](https://github.com/sqlalchemy/sqlalchemy) をインストール

!!! note
    python 3.11以降は [tomllib](https://docs.python.org/3/library/tomllib.html) を使用

!!! note
    エクストラは追加フォーマットや追加型のサポートを有効にします。必要なものだけを組み合わせてインストールできます。


## 最初のpyserdeクラスを定義

pyserdeの`@serde`デコレータを使用してクラスを定義します。  
モジュール名が `pyserde` ではなく `serde` であることに注意してください。  
`pyserde`は標準ライブラリの`dataclasses`モジュールに大きく依存しています。  
そのため、dataclassに慣れていない場合はまず[dataclassesのドキュメント](https://docs.python.org/3/library/dataclasses.html)を読むことをおすすめします。

```python
from serde import serde

@serde
class Foo:
    i: int
    s: str
    f: float
    b: bool
```

クラスがPythonインタプリタにロードされると、pyserdeは`@serde`によって（デ）シリアライズに必要なメソッドを生成します。  
コード生成は一度だけ行われ、クラスを使用する際にオーバーヘッドはありません。
これにより、クラスはpyserdeがサポートするすべてのデータ形式でシリアライズおよびデシリアライズ可能になります。

!!! note
    シリアライズまたはデシリアライズの機能のみが必要な場合、`@serde`デコレータの代わりに`@serialize`や`@deserialize`を使用できます。

    例：シリアライズのみを行う場合、`@serialize`デコレータを使用できます。しかし、`Foo`のデシリアライズAPI（例：`from_json`）を呼び出すとエラーが発生します。
    ```python
    from serde import serialize

    @serialize
    class Foo:
        i: int
        s: str
        f: float
        b: bool
    ```

## PEP585とPEP604

python>=3.10用の[PEP585](https://www.python.org/dev/peps/pep-0585/)スタイルのアノテーションと、[PEP604](https://www.python.org/dev/peps/pep-0604/) Unionオペレータがサポートされています。  
PEP585とPEP604を使用すると、pyserdeクラスをきれいに書くことができます。
```python
@serde
class Foo:
    a: int
    b: list[str]
    c: tuple[int, float, str, bool]
    d: dict[str, list[tuple[str, int]]]
    e: str | None
```

## pyserdeクラスの使用

次に、pyserdeの（デ）シリアライズAPIをインポートします。  
JSONの場合は以下のようにします。

```python
from serde.json import from_json, to_json
```

`to_json`を使用してオブジェクトをJSONにシリアライズします。
```python
f = Foo(i=10, s='foo', f=100.0, b=True)
print(to_json(f))
```

`from_json`に`Foo`クラスとJSON文字列を渡して、JSONをオブジェクトにデシリアライズします。
```python
s = '{"i": 10, "s": "foo", "f": 100.0, "b": true}'
print(from_json(Foo, s))
```

ファイルやネットワーク送信前にデータを加工したい場合、Pythonの`dict`としてシリアライズすることもできます。

```python
from serde import to_dict, from_dict

payload = to_dict(f)
# 例: 送信前にフィールドを追加する
payload["source"] = "cli"
print(from_dict(Foo, payload))
```

以上です！
pyserdeには他にも多くの機能があります。興味があれば、残りのドキュメントをお読みください。

!!! note
    YAML/TOML/MsgPackを使う場合は、上記の該当エクストラをインストールしてください。

!!! tip "どのタイプチェッカーを使用すべきか？"  
> pyserdeは[PEP681 dataclass_transform](https://peps.python.org/pep-0681/)に依存しています。  
> 2024年1月現在、[mypy](https://github.com/python/mypy)はdataclass_transformを完全にはサポートしていません。  
> 私の個人的なおすすめは[pyright](https://github.com/microsoft/pyright)です。
