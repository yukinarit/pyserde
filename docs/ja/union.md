# Union Representation

`pyserde>=0.7` では、Union が（デ）シリアライズされる方法を制御するための属性が提供されています。この概念は [serde-rs](https://serde.rs/enum-representations.html) にあるものと同じです。

これらの表現は dataclass にのみ適用され、dataclassではないオブジェクトは常に `Untagged` で（デ）シリアライズされます。

## `Untagged`

以下は、 `pyserde<0.7` におけるデフォルトの Union 表現です。dataclass が与えられた場合を例に上げます。

```python
@serde
class Bar:
    b: int

@serde
class Baz:
    b: int

@serde(tagging=Untagged)
class Foo:
    a: Union[Bar, Baz]
```

注意点として、`Bar` と `Baz` は同じフィールド名と型を持っています。  
`Foo(Baz(10))` を辞書にシリアライズすると、`{"a": {"b": 10}}` が得られます。

しかし、`{"a": {"b": 10}}` をデシリアライズすると、 `Foo(Baz(10))` ではなく `Foo(Bar(10))` が得られます。  
これは、pyserde が `Untagged` を使った Union の dataclass を正しく（デ）シリアライズ**できない**ことを意味します。

このため、pyserde は他の Union 表現オプションを提供しています。

## `ExternalTagging`

これは 0.7 以降のデフォルトの Union 表現です。`ExternalTagging` を使用したクラス宣言は以下のようになります。

```python
@serde(tagging=ExternalTagging)
class Foo:
    a: Union[Bar, Baz]
```
`Foo(Baz(10))` を辞書にシリアライズすると、 `{"a": {"Baz": {"b": 10}}}` が得られ、デシリアライズすると `Foo(Baz(10))` になります。

> **注意:** dataclass でないオブジェクトは、`tagging` 属性に関わらず常に `Untagged` で（デ）シリアライズされます。  
> これはタグに使用できる情報がないためです。`Untagged` の欠点は、特定のタイプを正しく非シリアライズできないことです。
>
> 例えば、以下のクラスの `Foo({1, 2, 3})` は `{"a": [1, 2, 3]}` にシリアライズされますが、デシリアライズすると `Foo([1, 2, 3])` になります。
>
> ```python
> @serde(tagging=ExternalTagging)
> class Foo:
>    a: Union[list[int], set[int]]
> ```

## `InternalTagging`

`InternalTagging` を使用したクラス宣言は以下のようになります。

```python
@serde(tagging=InternalTagging("type"))
class Foo:
    a: Union[Bar, Baz]
```

`Foo(Baz(10))` を辞書にシリアライズすると、`{"a": {"type": "Baz", "b": 10}}` が得られ、それを `Foo(Baz(10))` にデシリアライズできます。  
`type` タグは `Baz` の辞書内にエンコードされます。

## `AdjacentTagging`

`AdjacentTagging` を使用したクラス宣言は以下のようになります。

```python
@serde(tagging=AdjacentTagging("type", "content"))
class Foo:
    a: Union[Bar, Baz]
```

`Foo(Baz(10))` を辞書にシリアライズすると、`{"a": {"type": "Baz", "content": {"b": 10}}}` が得られ、それを `Foo(Baz(10))` にデシリアライズできます。`type` タグは `Baz` の辞書内にエンコードされ、`Baz` のフィールドは `content` 内にエンコードされます。


## Union 型の直接的な（デ）シリアライズ

v0.12.0 で新しく追加されました。

v0.12 以前において、（デ）シリアライズ API（例： `to_json`, `from_json`）に直接 Union 型のデータを渡すことは部分的にサポートされていましたが、Union 型は常にタグ無しとして扱われました。  
これは、利用者側で Union タグを変更することができなかったことを意味します。

以下の例は、タグ無しのため `Bar` に正しくデシリアライズできません。

```python
@serde
class Foo:
    a: int

@serde
class Bar:
    a: int

bar = Bar(10)
s = to_json(bar)
print(s)
# {"a": 10} を出力
print(from_json(Union[Foo, Bar], s))
# Foo(10) を出力
```

v0.12.0 以降、pyserde は（デ）シリアライズ API で渡された Union 型を適切に扱えます。  
Union 型は、pyserde のデフォルトのタグ付けである外部タグ付けとして扱われます。

以下の例は `Bar` として正しく（デ）シリアライズできます。

```python
@serde
class Foo:
    a: int

@serde
class Bar:
    a: int

bar = Bar(10)
s = to_json(bar, cls=Union[Foo, Bar])
print(s)
# {"Bar" {"a": 10}} を出力
print(from_json(Union[Foo, Bar], s))
# Bar(10) を出力
```

また、`serde.InternalTagging`、`serde.AdjacentTagging`、および `serde.Untagged` を使用してタグ付けを変更できます。

それでは、上記の例を用いてタグ付けを変更してみましょう。

タグ付けを変更するには、 `to_json` に新しい引数 `cls` を渡す必要があります。  
また、Unionクラスは `InternalTagging`、`AdjacentTagging`、または `Untagged` で必要なパラメータと共にラップされる必要があります。

* InternalTagging
  ```python
  from serde import InternalTagging

  s = to_json(bar, cls=InternalTagging("type", Union[Foo, Bar]))
  print(s)
  # {"type": "Bar", "a": 10} を出力
  print(from_json(InternalTagging("type", Union[Foo, Bar]), s))
  # Bar(10) を出力
  ```

* AdjacentTagging
  ```python
  from serde

  s = to_json(bar, cls=AdjacentTagging("type", "content", Union[Foo, Bar]))
  print(s)
  # {"type": "Bar", "content": {"a": 10}} を出力
  print(from_json(AdjacentTagging("type", "content", Union[Foo, Bar]), s))
  # Bar(10) を出力
  ```

* Untagged
  ```python
  from serde import Untagged

  s = to_json(bar, cls=Untagged(Union[Foo, Bar]))
  print(s)
  # {"a": 10} を出力
  print(from_json(Untagged(Union[Foo, Bar]), s))
  # Foo(10) を出力
  ```
