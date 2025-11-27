# 変更履歴

## 修正内容（2025-11-27）

### 新機能

#### 1. 日本語ファイルパス完全対応 🎌
**機能**: 日本語を含むファイルパスに完全対応

**実装**:
- `pathlib.Path` を使用したパス正規化
- チルダ展開（`~`）の自動処理
- 相対パス・絶対パスの適切な処理
- Unicode正規化

**対応パス**:
```python
# 全て正常に処理可能
"~/デスクトップ/データ.csv"
"./日本語フォルダ/ファイル.csv"
"/Users/yamada/ドキュメント/参加者.csv"
```

**技術詳細**:
```python
# 修正前（os.path）
if not os.path.exists(csv_path):
    # 日本語パスで問題が発生する可能性

# 修正後（pathlib.Path）
csv_path = Path(csv_path).expanduser().resolve()
if not csv_path.exists():
    # 日本語パスも完全に対応
```

#### 2. エンコーディング検出の大幅改善 🔍
**追加エンコーディング**:
- **UTF-16**（connpass等のエクスポート）
- **UTF-16 LE**（Little Endian）
- **UTF-16 BE**（Big Endian）
- Shift_JIS（レガシー日本語システム）

**区切り文字の自動検出**:
- カンマ区切り（CSV）
- タブ区切り（TSV）

**検出プロセス**:
```python
encodings = ['utf-8', 'utf-8-sig', 'utf-16', 'utf-16-le', 'utf-16-be', 'cp932', 'shift_jis']
separators = [',', '\t']

for encoding in encodings:
    for sep in separators:
        # 全組み合わせを試行
```

**対応ファイル形式**:
- CSV（カンマ区切り）
- TSV（タブ区切り）
- UTF-8, UTF-16, CP932, Shift_JIS エンコーディング

### バグ修正

#### 1. NaN値のJSON変換エラー
**問題**: CSV内のNaN値がJSON変換時にエラーを引き起こす
```
ValueError: Out of range float values are not JSON compliant: nan
```

**解決策**:
- `df.fillna('')` を使用してNaN値を空文字列に置換
- Google Sheets API へのデータ送信前に処理

**影響**:
- 空のセル（NaN）を含むCSVファイルが正常に処理可能に

#### 2. パフォーマンス改善
**変更前**:
- 1行ずつ `append_row()` で書き込み
- 12行のデータで12回のAPI呼び出し

**変更後**:
- `worksheet.update()` で一括書き込み
- 12行のデータで1回のAPI呼び出し

**効果**:
- API呼び出し回数を大幅削減（行数に比例）
- 書き込み速度が劇的に向上
- API レート制限に達するリスクを軽減

#### 3. 変数名の修正
**問題**: `spreadsheet_name` が未定義
**解決策**: `spreadsheet_id` を使用するように修正

### 技術詳細

```python
# 修正前
data_rows = df.values.tolist()
for row in data_rows:
    worksheet.append_row(row)  # N回のAPI呼び出し

# 修正後
df = df.fillna('')  # NaN対策
header = df.columns.tolist()
data_rows = df.values.tolist()
all_data = [header] + data_rows
worksheet.update('A1', all_data, value_input_option='RAW')  # 1回のAPI呼び出し
```

### ベストプラクティス

1. **データクリーニング**: API送信前にデータを検証・変換
2. **バッチ処理**: 可能な限り一括操作を使用
3. **エラーハンドリング**: JSON互換性のないデータ型を事前に処理
