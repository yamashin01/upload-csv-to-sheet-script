# 日本語パス対応ガイド

## 概要

`csv_to_sheets.py` は日本語を含むファイルパスに完全対応しています。

## 対応内容

### 1. パス正規化

`pathlib.Path` を使用した堅牢なパス処理：

```python
# 修正前（os.path）
if not os.path.exists(csv_path):
    print(f"エラー: {csv_path} が見つかりません")
    sys.exit(1)

# 修正後（pathlib.Path）
csv_path = Path(csv_path).expanduser().resolve()
if not csv_path.exists():
    print(f"エラー: {csv_path} が見つかりません")
    sys.exit(1)
```

### 2. 対応するパス形式

#### チルダ展開（`~`）
```bash
~/デスクトップ/データ.csv
~/ドキュメント/売上_2024.csv
~/ダウンロード/認証情報.json
```

#### 相対パス
```bash
./日本語フォルダ/ファイル.csv
../親フォルダ/データ.csv
sample/イベント参加者.csv
```

#### 絶対パス
```bash
/Users/yamada/デスクトップ/参加者リスト.csv
/Users/yamada/Documents/データ/売上.csv
```

### 3. エンコーディング自動検出

以下の順序でエンコーディングを試行：

1. **UTF-8**（推奨）
2. **UTF-8 with BOM**（Excelエクスポート）
3. **CP932**（Windows日本語）
4. **Shift_JIS**（レガシー日本語）

```python
try:
    df = pd.read_csv(str(csv_path), encoding='utf-8')
except UnicodeDecodeError:
    try:
        df = pd.read_csv(str(csv_path), encoding='utf-8-sig')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(str(csv_path), encoding='cp932')
        except UnicodeDecodeError:
            df = pd.read_csv(str(csv_path), encoding='shift_jis')
```

## 使用例

### 基本的な使用

```bash
# 日本語ファイル名
python csv_to_sheets.py "~/デスクトップ/参加者リスト.csv" "1abc123def456"

# 日本語認証情報パス
python csv_to_sheets.py data.csv "1abc123def456" -c "~/ダウンロード/認証情報.json"

# 日本語シート名
python csv_to_sheets.py data.csv "1abc123def456" --sheet "参加者一覧"
```

### 複雑なパス

```bash
# スペースと日本語を含むパス
python csv_to_sheets.py "~/デスクトップ/イベント データ/参加者 2024.csv" "1abc123def456"

# 複数レベルの日本語フォルダ
python csv_to_sheets.py "~/ドキュメント/プロジェクト/イベント管理/データ/参加者.csv" "1abc123def456"
```

## 技術詳細

### pathlib.Path のメリット

1. **クロスプラットフォーム対応**: Windows/macOS/Linux で同じコードが動作
2. **Unicode 完全対応**: 日本語、中国語、韓国語などの多言語パスを処理
3. **パス操作の簡潔性**: 直感的な API
4. **型安全性**: Path オブジェクトとして扱える

### 実装の詳細

```python
def read_csv(csv_path):
    """CSVファイルを読み込む（日本語パス対応）"""
    # パスを正規化（~展開、絶対パス化、日本語パス対応）
    csv_path = Path(csv_path).expanduser().resolve()

    if not csv_path.exists():
        print(f"エラー: {csv_path} が見つかりません")
        sys.exit(1)

    # str()でパス文字列に変換してpandasに渡す
    df = pd.read_csv(str(csv_path), encoding='utf-8')
    return df
```

### Path メソッドの役割

| メソッド | 役割 | 例 |
|----------|------|-----|
| `expanduser()` | `~` をホームディレクトリに展開 | `~/デスクトップ` → `/Users/yamada/デスクトップ` |
| `resolve()` | 相対パスを絶対パスに変換 | `./data.csv` → `/Users/yamada/.../data.csv` |
| `exists()` | ファイル/ディレクトリの存在確認 | `True` or `False` |
| `parent` | 親ディレクトリを取得 | `/Users/yamada/デスクトップ/data.csv` → `/Users/yamada/デスクトップ` |
| `name` | ファイル名を取得 | `/Users/yamada/デスクトップ/data.csv` → `data.csv` |

## トラブルシューティング

### macOS

通常は自動的に対応。特別な設定は不要です。

### Windows

ファイルシステムが UTF-8 をサポートしていることを確認：

```bash
# PowerShell で確認
[Console]::OutputEncoding
```

### Linux

ロケールが UTF-8 に設定されていることを確認：

```bash
locale
# LANG=ja_JP.UTF-8 または LANG=en_US.UTF-8
```

## テスト方法

テストスクリプトを実行：

```bash
python3 test_japanese_paths.py
```

期待される出力：
```
============================================================
日本語パス処理テスト
============================================================

入力パス: ~/デスクトップ/test.csv
  ✅ 正規化パス: /Users/yamada/デスクトップ/test.csv
  📁 存在確認: False
  📝 親ディレクトリ: /Users/yamada/デスクトップ
  📄 ファイル名: test.csv
...
```

## パフォーマンス

日本語パス処理によるパフォーマンスへの影響はほぼゼロです：

- パス正規化: O(1)
- 存在確認: O(1)
- 文字列変換: O(n)（n=パス長）

## ベストプラクティス

### 推奨

✅ 引用符でパスを囲む
```bash
python csv_to_sheets.py "~/デスクトップ/データ.csv" "1abc123def456"
```

✅ 相対パスより絶対パスまたは `~` を使用
```bash
python csv_to_sheets.py "~/ドキュメント/data.csv" "1abc123def456"
```

✅ UTF-8 エンコーディングのCSVを使用

### 非推奨

❌ 引用符なしでスペースを含むパス
```bash
python csv_to_sheets.py ~/デスクトップ/データ 2024.csv "1abc123def456"  # エラー
```

❌ バックスラッシュ（Windows スタイル）
```bash
python csv_to_sheets.py C:\Users\yamada\データ.csv "1abc123def456"  # macOS/Linux では不可
```

## まとめ

- ✅ 日本語パス完全対応
- ✅ チルダ展開、相対パス、絶対パス対応
- ✅ 複数エンコーディング自動検出
- ✅ クロスプラットフォーム対応
- ✅ パフォーマンスへの影響なし
