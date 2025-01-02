# Type Checking

pyserdeはv0.9からランタイム型チェックを提供しています。  
v0.14で完全に作り直され、[beartype](https://github.com/beartype/beartype)を使用してより洗練され信頼性の高いものとなりました。  
型安全で堅牢なプログラムを書くためには、型チェックを常に有効にすることを強く推奨します。

## `strict`

厳格な型チェック `strict` は、（デ）シリアライズとオブジェクト構築の際にすべてのフィールド値を宣言された型と照合します。  
これはv0.14以降のデフォルトの型チェックモードです。

このモードでは、クラス属性を指定せずに `@serde` デコレータを使用してクラスを宣言した場合、`@serde(type_check=strict)` と見なされ、厳格な型チェックが有効になります。

```python
@serde
class Foo:
    s: str
```

例えば、以下のように間違った型のオブジェクトで`Foo`を呼び出すと、
```python
foo = Foo(10)
```

以下のエラーが発生します。
```python
beartype.roar.BeartypeCallHintParamViolation: Method __main__.Foo.__init__() parameter s=10 violates type hint <class 'str'>, as int 10 not instance of str.
```

> **注記:** 2024年2月時点でbeartypeは検証フックを提供していないため、コンストラクターからはSerdeErrorではなくbeartypeの例外が発生します。

同様に、間違った型のオブジェクトで（デ）シリアライズAPIを呼び出すと、

```python
print(to_json(foo))
```

再びエラーが発生します。

```python
serde.compat.SerdeError: Method __main__.Foo.__init__() parameter s=10 violates type hint <class 'str'>, as int 10 not instance of str.
```

> **注記:** beartypeによる型チェックにはいくつかの注意点があります。
>
> 1. beartypeは変更されたプロパティを検証できません。
>
>   以下のコードでは、プロパティ `s` が最後に変更されていますが、beartypeはこのケースを検出できません。
>   ```python
>   @serde
>   class Foo:
>       s: str
>
>   f = Foo("foo")
>   f.s = 100
>   ```
>
> 2. beartypeはコンテナ内の各要素を検証することはできません。これはバグではなく、beartypeの設計原則です。[Does beartype actually do anything?](https://beartype.readthedocs.io/en/latest/faq/#faq-o1)を参照してください。

## `coerce`

型強制 `coerce` は、（デ）シリアライズ中に値を宣言された型に自動的に変換します。

```python
@serde(type_check=coerce)
class Foo:
    s: str

foo = Foo(10)
# pyserdeは自動的に int 値の 10 を str の "10" に変換します
# {"s": "10"}が出力されます
print(to_json(foo))
```

しかし、値が宣言された型に変換できない場合（例えば、値が `foo` で型が `int` の場合）、pyserde は`SerdeError` を発生させます。

## `disabled`

これはpyserde v0.8.3およびv0.9.xまでのデフォルトの挙動です。  
型強制またはチェックは実行されません。

利用者が間違った値を入力しても、pyserdeは型の不整合を無視して処理を続行します。

```python
@serde
class Foo:
    s: str

foo = Foo(10)
# pyserdeは型の整合性を確認しないため、{"s": 10} が出力されます
print(to_json(foo))
```
