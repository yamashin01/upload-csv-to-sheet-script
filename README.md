# CSV to Google Sheets - CSVデータのスプレッドシート出力ツール

CSVファイルを、自動でGoogleスプレッドシートに出力するPythonスクリプトです。

## 主な機能

- CSVファイルを読み込んでGoogleスプレッドシートに出力
- 日本語ファイルパス完全対応（例: `~/デスクトップ/データ.csv`）
- 一括アップロード機能（csv_files/内の全CSVを自動処理）
- **🆕 Google Apps Script (GAS) 自動実行機能**（CSVアップロード後にGASスクリプトを実行）
- 複数のエンコーディング形式に自動対応（UTF-8, UTF-8-BOM, UTF-16, CP932, Shift_JIS）
- 区切り文字自動検出（カンマ、タブ）
- 複数のシート管理に対応
- ドライラン機能でプレビュー確認可能
- 既存データの上書きまたは追記を選択可能

---

## クイックスタート（5分）

### 1. セットアップ

```bash
# Python仮想環境を作成
python3 -m venv csv_to_sheets_env
source csv_to_sheets_env/bin/activate

# 必要なライブラリをインストール
pip install --upgrade pip
pip install gspread google-auth-oauthlib google-auth-httplib2 pandas
```

### 2. Google Cloud設定

#### Google Sheets APIを有効化
1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクトを作成
2. 「APIとサービス」→「ライブラリ」→「Google Sheets API」を検索して有効化
3. 「Google Drive API」も同様に有効化

#### サービスアカウントを作成
1. 「APIとサービス」→「認証情報」→「認証情報を作成」→「サービスアカウント」
2. サービスアカウント名を入力（例: `csv-to-sheets`）
3. ロール: 「基本」→「編集者」を選択
4. 「キー」タブ→「キーを追加」→「JSON」を選択してダウンロード
5. ダウンロードしたJSONファイルを `credentials.json` にリネームしてプロジェクトディレクトリに配置

#### スプレッドシートを共有
1. Googleドライブで出力先となるスプレッドシートを開く
2. `credentials.json` をテキストエディタで開き、`"client_email"` の値をコピー
3. スプレッドシートの「共有」をクリックし、コピーしたメールアドレスを編集者として追加

### 3. 実行

#### 単一ファイルをアップロード
```bash
# 仮想環境を有効化
source csv_to_sheets_env/bin/activate

# スクリプトを実行
python csv_to_sheets.py <CSVファイルパス> "<スプレッドシートID>" --sheet "シート名"
```

#### 複数ファイルを一括アップロード
```bash
# 実行権限を付与（初回のみ）
chmod +x batch_upload.sh

# batch_upload.sh を編集してスプレッドシートIDを設定
# 設定セクション:
#   SPREADSHEET_ID="あなたのスプレッドシートID"

# 一括アップロード実行
./batch_upload.sh
```

---

## 使い方

### スプレッドシートIDの取得方法

GoogleドライブでスプレッドシートのURLを確認：
```
https://docs.google.com/spreadsheets/d/1abc123def456xyz/edit#gid=0
                                        ↑↑↑↑↑↑↑↑↑↑↑↑↑
                                        このID部分
```

### コマンドオプション

| オプション | 短縮形 | 説明 | デフォルト |
|-----------|--------|------|-----------|
| `csv_path` | - | CSVファイルのパス（必須） | - |
| `spreadsheet_id` | - | スプレッドシートのURL またはID（必須） | - |
| `--sheet` | `-s` | 出力先のシート名 | `Sheet1` |
| `--credentials` | `-c` | Google認証情報ファイルのパス | `credentials.json` |
| `--no-clear` | - | 既存データをクリアせず追記 | （クリアする） |
| `--dry-run` | `-d` | ドライラン（プレビューのみ） | （実行） |

### 実行例

#### 例1: URLを指定
```bash
python csv_to_sheets.py data/participants.csv "https://docs.google.com/spreadsheets/d/1abc123def456/edit"
```

#### 例2: IDとシート名を指定
```bash
python csv_to_sheets.py data/participants.csv "1abc123def456" --sheet "参加者リスト"
```

#### 例3: 日本語パスに対応
```bash
python csv_to_sheets.py "~/デスクトップ/イベント参加者.csv" "1abc123def456"
```

#### 例4: ドライラン
```bash
python csv_to_sheets.py data/test.csv "1abc123def456" --dry-run
```

#### 例5: 既存データに追記
```bash
python csv_to_sheets.py data/new_data.csv "1abc123def456" --sheet "全イベント" --no-clear
```

---

## 一括アップロード機能

### batch_upload.sh の使い方

`csv_files/` ディレクトリ内の全CSVファイルを自動でアップロードするシェルスクリプトです。

#### 1. 設定を編集

`batch_upload.sh` をテキストエディタで開き、設定セクションを編集：

```bash
# ============================================================================
# 設定セクション - ここを編集してください
# ============================================================================

# GoogleスプレッドシートID
SPREADSHEET_ID="1Rv_V1jEe8DUMxAk_94bl7TqZa6lRVR5qCgoMx9GKHnU"

# Google認証情報ファイルのパス
CREDENTIALS="credentials.json"
```

#### 2. 実行

```bash
./batch_upload.sh
```

#### 3. 実行フロー

1. **前提条件チェック**: Pythonスクリプト、仮想環境、認証情報の確認
2. **CSVファイル検出**: csv_files/ 内の全 .csv ファイルを検索
3. **確認プロンプト**: アップロード対象ファイルを表示して確認
4. **各ファイルの処理**: CSVファイル名をシート名として使用し、順次アップロード
5. **結果サマリー**: 成功/失敗の件数と詳細を表示

#### シート名の生成ルール

CSVファイル名から `.csv` 拡張子を除いた部分がシート名になります：

| CSVファイル名 | 生成されるシート名 |
|--------------|------------------|
| `event-attendee-978320.csv` | `event-attendee-978320` |
| `event_306730_participants.csv` | `event_306730_participants` |
| `データ_2024.csv` | `データ_2024` |

---

## 対応エンコーディング・区切り文字

### エンコーディング（自動検出）
1. **UTF-8**（推奨）
2. **UTF-8 with BOM**（Excelエクスポート）
3. **UTF-16**（connpass, Peatixエクスポート）
4. **UTF-16 LE/BE**（Unicode）
5. **CP932**（Windows日本語）
6. **Shift_JIS**（レガシー日本語）

### 区切り文字（自動検出）
1. **カンマ** (`,`) - CSV形式
2. **タブ** (`\t`) - TSV形式

スクリプトは自動的に正しいエンコーディングと区切り文字を検出します。

---

## 🚀 Google Apps Script (GAS) 自動実行機能

CSVアップロード後に、スプレッドシートに紐付けられたGASスクリプトを自動実行できます。

### 簡単セットアップ

1. **GASスクリプトを準備**（スプレッドシートの「拡張機能」→「Apps Script」）
2. **Script IDを取得**（「プロジェクトの設定」→「Script ID」）
3. **batch_upload.shで設定**:

```bash
EXECUTE_GAS=true
GAS_SCRIPT_ID="AKfycbyXXXXXXXXXXXXX"
GAS_FUNCTION="onDataUploaded"
GAS_PARAMS='["Sheet1", 100]'  # オプション
```

4. **実行**: `./batch_upload.sh`

### 詳細ガイド

GAS実行機能の詳細なセットアップ手順は [GAS_EXECUTION_GUIDE.md](GAS_EXECUTION_GUIDE.md) をご覧ください：

- 認証情報の設定方法
- GASスクリプトの作成例
- デプロイメント手順
- トラブルシューティング

---

## トラブルシューティング

### エラー: `ModuleNotFoundError: No module named 'pandas'`

**原因**: 仮想環境が有効になっていない

**解決策**:
```bash
source csv_to_sheets_env/bin/activate
```

### エラー: `Google Sheets API has not been used`

**原因**: Google Sheets APIが有効になっていない

**解決策**:
[Google Cloud Console](https://console.developers.google.com/apis/api/sheets.googleapis.com/overview) で API を有効化

### エラー: `credentials.json が見つかりません`

**原因**: 認証情報ファイルが見つからない

**解決策**:
```bash
# パスを指定して実行
python csv_to_sheets.py data.csv "1abc123" -c ~/Downloads/credentials.json
```

### エラー: `スプレッドシートID 'XXX' が見つかりません`

**原因**: スプレッドシートIDが正しくない、またはサービスアカウントに権限がない

**解決策**:
1. URLからIDを正確にコピー
2. スプレッドシートの共有設定で、`client_email` が編集者として追加されているか確認
3. 共有後、数秒待ってから再実行

### エラー: `文字化けが発生する`

**原因**: CSVファイルのエンコーディングが特殊

**スクリプトの対応**: 自動的に複数のエンコーディングを試行

**確認方法**:
```bash
# ファイルのエンコーディングを確認
file yourfile.csv
```

それでも失敗する場合：
1. CSVファイルをExcelで開く
2. 「名前を付けて保存」→「CSV UTF-8（カンマ区切り）」を選択
3. 再度スクリプトを実行

---

## ディレクトリ構成

```
python-csv_to_sheets/
├── csv_to_sheets_env/           # Python仮想環境
├── csv_to_sheets.py             # メインスクリプト
├── execute_gas.py               # 🆕 GAS実行スクリプト
├── batch_upload.sh              # 一括アップロードスクリプト（GAS実行統合済み）
├── credentials.json             # Google認証情報（自分で配置）
├── requirements.txt             # Python依存ライブラリ
├── csv_files/                   # CSVファイル配置用ディレクトリ
│   ├── event-attendee-978320.csv
│   ├── event_306730_participants.csv
│   └── ...
├── README.md
└── GAS_EXECUTION_GUIDE.md       # 🆕 GAS実行機能の詳細ガイド
```


## 注意事項

- **Google認証情報の管理**: `credentials.json` は機密情報です。GitHubなどのリポジトリにコミットしないでください
- **APIの利用制限**: Google Sheets APIは無料版で一定の利用制限があります。大規模データ処理の場合は注意してください
- **スプレッドシートの権限**: スクリプトを実行するサービスアカウントがスプレッドシートの編集権限を持っていることを確認してください

---

## 動作環境

- **対応OS**: macOS、Linux、Windows
- **Python バージョン**: Python 3.8以上
- **対応ファイル形式**: CSV（UTF-8, UTF-8 BOM, UTF-16, Shift-JIS, CP932）

---

## 更新履歴

### v1.4.0 🆕
- **Google Apps Script (GAS) 自動実行機能を追加**
  - `execute_gas.py`: GASスクリプトを外部から実行
  - `batch_upload.sh`: CSVアップロード後にGASを自動実行
  - Apps Script API統合
  - パラメータ付き関数実行に対応
- 詳細ガイド（`GAS_EXECUTION_GUIDE.md`）を追加
- `requirements.txt`: `google-api-python-client` を追加

### v1.3.0
- 一括アップロードスクリプト（batch_upload.sh）を追加
- スクリプト内設定方式に変更（引数不要）

### v1.2.0
- UTF-16エンコーディング対応を追加
- タブ区切り（TSV）形式の自動検出機能を追加

### v1.1.0
- 日本語ファイルパス対応
- pathlibによるクロスプラットフォーム互換性向上

### v1.0.0
- 基本的なCSV→スプレッドシート出力機能
- 複数エンコーディング対応
- ドライラン機能
- 追記機能

---

## ライセンス

このスクリプトは自由に利用・改変できます。
