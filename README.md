# CSV to Google Sheets - Peatix/connpass参加者データ自動化ツール

Peatix、connpass などのイベントサイトからダウンロードしたCSVファイルを、自動でGoogleスプレッドシートに出力するPythonスクリプトです。

## 概要

- **対応ファイル形式**: CSV（UTF-8, UTF-8 BOM, Shift-JIS）
- **出力先**: Googleスプレッドシート
- **動作環境**: macOS、Linux、Windows
- **推奨Python バージョン**: Python 3.8以上

## 主な機能

- ✅ CSVファイルを読み込んでGoogleスプレッドシートに出力
- ✅ **日本語ファイルパス完全対応**（例: `~/デスクトップ/データ.csv`）
- ✅ 複数のシート管理に対応
- ✅ ドライラン機能でプレビュー確認可能
- ✅ 既存データの上書きまたは追記を選択可能
- ✅ 複数のエンコーディング形式に自動対応（UTF-8, UTF-8-BOM, CP932, Shift_JIS）
- ✅ NaN（空セル）の適切な処理
- ✅ 高速一括書き込み（API呼び出し最適化）
- ✅ わかりやすいエラーメッセージ

## セットアップ

### 1. Google Cloud Projectの設定

#### 1.1 Google Cloud Consoleでプロジェクト作成

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 画面上部の「プロジェクトを選択」をクリック
3. 「新しいプロジェクト」を選択し、プロジェクト名を入力して作成

#### 1.2 Google Sheets APIを有効化

1. Cloud Consoleで作成したプロジェクトを選択
2. 左メニューの「APIとサービス」→「ライブラリ」をクリック
3. 検索ボックスで「Google Sheets API」を検索
4. 「Google Sheets API」をクリックして「有効にする」ボタンをクリック

#### 1.3 サービスアカウントを作成

1. 「APIとサービス」→「認証情報」をクリック
2. 「認証情報を作成」→「サービスアカウント」を選択
3. 以下の情報を入力（その他は任意）
   - サービスアカウント名: `csv-to-sheets` など
4. 「作成して続行」をクリック
5. ロール: 「基本」→「編集者」を選択
6. 「続行」→「完了」をクリック

#### 1.4 JSONキーをダウンロード

1. 「APIとサービス」→「認証情報」をクリック
2. 「サービスアカウント」セクションで作成したアカウントをクリック
3. 「キー」タブをクリック
4. 「キーを追加」→「新しいキーを作成」
5. キーのタイプで「JSON」を選択して「作成」
6. JSONファイル（`credentials.json`）がダウンロードされます

#### 1.5 スプレッドシートを共有

1. Googleドライブで対象のスプレッドシートを開く
2. スプレッドシートのURLからIDをコピー（後で使用）
3. 右上の「共有」をクリック
4. ダウンロードした`credentials.json`をテキストエディタで開く
5. `"client_email"` の値（例: `xxx@xxx.iam.gserviceaccount.com`）をコピー
6. スプレッドシートの共有ダイアログにメールアドレスをペーストして、編集者として追加

### 2. Python環境の準備

#### 2.1 ターミナルを開く

Macbookで「ターミナル」アプリを開きます。

#### 2.2 作業ディレクトリを作成

```bash
mkdir csv_to_sheets
cd csv_to_sheets
```

#### 2.3 仮想環境を作成（推奨）

```bash
python3 -m venv csv_to_sheets_env
source csv_to_sheets_env/bin/activate
```

仮想環境が有効になると、ターミナルプロンプトの前に `(csv_to_sheets_env)` と表示されます。

#### 2.4 必要なライブラリをインストール

```bash
pip install --upgrade pip
pip install gspread google-auth-oauthlib google-auth-httplib2 pandas
```

#### 2.5 ファイルを配置

- `csv_to_sheets.py` をこの作業ディレクトリに配置
- `credentials.json` をこの作業ディレクトリに配置
- ダウンロードしたCSVファイルを `data/` フォルダなど、わかりやすい場所に配置

### 3. ディレクトリ構成例

```
csv_to_sheets/
├── csv_to_sheets_env/          # 仮想環境フォルダ
├── csv_to_sheets.py             # メインスクリプト
├── credentials.json             # Google認証情報（自分のGCPプロジェクトのもの）
├── data/                        # CSVファイルを配置するフォルダ
│   ├── participants_peatix.csv
│   └── participants_connpass.csv
└── README.md
```

## 使い方

### 基本的な実行方法

```bash
# 1. 仮想環境を有効化（毎回の実行時に必要）
source csv_to_sheets_env/bin/activate

# 2. スクリプトを実行（URLまたはIDを指定）
python csv_to_sheets.py <CSVファイルパス> "<スプレッドシートURL or ID>"
```

### 実行例

#### 例1: スプレッドシートのURLを指定

```bash
python csv_to_sheets.py data/participants.csv "https://docs.google.com/spreadsheets/d/1abc123def456/edit#gid=0"
```

#### 例2: スプレッドシートのIDを指定

```bash
python csv_to_sheets.py data/participants.csv "1abc123def456"
```

#### 例3: シート名を指定

```bash
python csv_to_sheets.py data/participants.csv "1abc123def456" --sheet "Peatix_20240101"
```

#### 例4: ドライラン（プレビューのみ）

```bash
python csv_to_sheets.py data/participants.csv "1abc123def456" --dry-run
```

## コマンドオプション一覧

| オプション | 短縮形 | 説明 | デフォルト |
|-----------|--------|------|-----------|
| `csv_path` | - | CSVファイルのパス（必須） | - |
| `spreadsheet_id` | - | スプレッドシートのURL またはID（必須） | - |
| `--sheet` | `-s` | 出力先のシート名 | `Sheet1` |
| `--credentials` | `-c` | Google認証情報ファイルのパス | `credentials.json` |
| `--no-clear` | - | 既存データをクリアせず追記 | （クリアする） |
| `--dry-run` | `-d` | ドライラン（プレビューのみ） | （実行） |
| `--help` | `-h` | ヘルプを表示 | - |

### スプレッドシートIDの取得方法

Googleドライブでスプレッドシートを開いた時のURLから、IDを取得できます：

```
https://docs.google.com/spreadsheets/d/1abc123def456xyz/edit#gid=0
                                        ↑↑↑↑↑↑↑↑↑↑↑↑↑
                                        このID部分を使用
```

スクリプトでは以下のいずれでも指定可能です：
- **完全なURL**: `https://docs.google.com/spreadsheets/d/1abc123def456xyz/edit`
- **IDのみ**: `1abc123def456xyz`

## 日本語パス対応

このスクリプトは日本語を含むファイルパスに完全対応しています：

### 対応するパス形式

```bash
# チルダ展開（ホームディレクトリ）
~/デスクトップ/イベント参加者.csv
~/ドキュメント/売上データ_2024.csv

# 相対パス
./日本語フォルダ/ファイル.csv
../親フォルダ/データ.csv

# 絶対パス
/Users/yamada/デスクトップ/参加者リスト.csv
```

### エンコーディング・区切り文字自動検出

以下のエンコーディングと区切り文字を自動検出して処理します：

**エンコーディング**:
1. **UTF-8**（推奨）
2. **UTF-8 with BOM**（Excelエクスポート）
3. **UTF-16**（connpass, Peatixエクスポート）
4. **UTF-16 LE/BE**（Unicode）
5. **CP932**（Windows日本語）
6. **Shift_JIS**（レガシー日本語）

**区切り文字**:
1. **カンマ** (`,`) - CSV形式
2. **タブ** (`\t`) - TSV形式

### 使用例

```bash
# 日本語ファイル名のCSVを読み込み
python csv_to_sheets.py "~/デスクトップ/イベント参加者_2024.csv" "1abc123def456"

# 日本語の認証情報パス
python csv_to_sheets.py data.csv "1abc123def456" -c "~/ダウンロード/認証情報.json"

# 日本語シート名
python csv_to_sheets.py data.csv "1abc123def456" --sheet "参加者一覧"
```

## よく使うコマンド集

```bash
# 仮想環境の有効化
source csv_to_sheets_env/bin/activate

# 仮想環境の終了
deactivate

# ヘルプを表示
python csv_to_sheets.py --help

# パスにスペースや日本語が含まれる場合は引用符で囲む
python csv_to_sheets.py "~/Downloads/participants list.csv" "参加者管理"
python csv_to_sheets.py "~/ダウンロード/参加者リスト.csv" "1abc123def456"
```

## トラブルシューティング

### エラー: `credentials.json が見つかりません`

**原因**: 認証情報ファイルがスクリプトと同じディレクトリにないか、パスが正しくない

**解決策**:
```bash
# 1. credentials.json が存在するか確認
ls -la credentials.json

# 2. パスを指定して実行
python csv_to_sheets.py data/participants.csv "参加者管理" -c ~/Downloads/credentials.json
```

### エラー: `スプレッドシートID 'XXX' が見つかりません`

**原因**: スプレッドシートIDが正しくないか、サービスアカウントに権限がない

**解決策**:
1. Googleドライブで対象のスプレッドシートを開く
2. URLからIDを正確にコピー（`https://docs.google.com/spreadsheets/d/{ID}/edit` の{ID}部分）
3. スプレッドシートの共有設定で、`client_email` が編集者として追加されているか確認
4. 共有後、数秒待ってから再実行

**IDの確認方法**:
```bash
# スプレッドシートを開いたURLの例
https://docs.google.com/spreadsheets/d/1abc123def456xyz/edit#gid=0

# IDのみを指定
python csv_to_sheets.py data/participants.csv "1abc123def456xyz"

# または完全なURLで指定
python csv_to_sheets.py data/participants.csv "https://docs.google.com/spreadsheets/d/1abc123def456xyz/edit"
```

### エラー: `文字化けが発生する` または `エンコーディングを自動検出できませんでした`

**原因**: CSVファイルのエンコーディングが特殊

**スクリプトの対応**: 自動的に以下を試みます
- エンコーディング: UTF-8, UTF-8-BOM, UTF-16, UTF-16-LE, UTF-16-BE, CP932, Shift-JIS
- 区切り文字: カンマ (`,`), タブ (`\t`)

**確認方法**:
```bash
# ファイルのエンコーディングを確認
file yourfile.csv

# 例: UTF-16の場合
# yourfile.csv: Unicode text, UTF-16, little-endian text
```

ほとんどの場合は自動対応しますが、それでも失敗する場合：
1. CSVファイルをExcelで開く
2. 「名前を付けて保存」→「CSV UTF-8（カンマ区切り）」を選択
3. 再度スクリプトを実行

### エラー: `ドライランでは成功したが、実行時にエラーが出る`

**原因**: スプレッドシートの権限不足または接続エラー

**解決策**:
```bash
# 1. ドライランで何度か確認
python csv_to_sheets.py data/participants.csv "参加者管理" --dry-run

# 2. 権限を確認してから実行
python csv_to_sheets.py data/participants.csv "参加者管理"

# 3. エラーメッセージをコピーして問い合わせ
```

### エラー: `ModuleNotFoundError: No module named 'gspread'`

**原因**: ライブラリがインストールされていない

**解決策**:
```bash
# 仮想環境が有効になっているか確認（プロンプトに (csv_to_sheets_env) があるか）
source csv_to_sheets_env/bin/activate

# ライブラリを再インストール
pip install gspread google-auth-oauthlib google-auth-httplib2 pandas
```

## ワークフロー例

### Peatix参加者データを毎月スプレッドシートに出力する

1. Peatixの管理画面から参加者リストをCSVダウンロード
2. ダウンロードファイルを `data/participants_202401.csv` にリネーム
3. 対象のGoogleスプレッドシートを開き、URLからIDをコピー
4. 以下のコマンドを実行

```bash
source csv_to_sheets_env/bin/activate
python csv_to_sheets.py data/participants_202401.csv "1abc123def456xyz" --sheet "202401月"
```

### 複数イベントのデータを1つのスプレッドシートに統合

```bash
# Peatixデータを追記
python csv_to_sheets.py data/peatix_event1.csv "1abc123def456xyz" --sheet "全イベント" --no-clear

# connpassデータを追記
python csv_to_sheets.py data/connpass_event1.csv "1abc123def456xyz" --sheet "全イベント" --no-clear
```

## 注意事項

- **Google認証情報の管理**: `credentials.json` は機密情報です。GitHubなどのリポジトリにコミットしないでください
- **APIの利用制限**: Google Sheets APIは無料版で一定の利用制限があります。大規模データ処理の場合は注意してください
- **スプレッドシートの権限**: スクリプトを実行するユーザーがスプレッドシートの編集権限を持っていることを確認してください

## サポート

スクリプト実行時にエラーが発生した場合：

1. エラーメッセージ全文をコピー
2. ドライランモード（`--dry-run`）で確認
3. トラブルシューティングセクションを参照

## ライセンス

このスクリプトは自由に利用・改変できます。

## 更新履歴

**v1.0.0** (初版)
- 基本的なCSV→スプレッドシート出力機能
- 複数エンコーディング対応
- ドライラン機能
- 追記機能# upload-csv-to-sheet-script
