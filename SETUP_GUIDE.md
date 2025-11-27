# Google Sheets API セットアップガイド

## 前提条件

このスクリプトを使用するには、以下が必要です：

1. Google Cloud プロジェクト
2. サービスアカウント認証情報（JSONファイル）
3. Google Sheets API と Google Drive API の有効化

## セットアップ手順

### 1. Google Sheets API を有効化

エラーメッセージに表示された URL にアクセス：
```
https://console.developers.google.com/apis/api/sheets.googleapis.com/overview?project=429713708426
```

「有効にする」ボタンをクリックして、数分待ちます。

### 2. Google Drive API を有効化

1. [API ライブラリ](https://console.cloud.google.com/apis/library?project=429713708426) にアクセス
2. 「Google Drive API」を検索
3. 「有効にする」ボタンをクリック

### 3. サービスアカウントのメールアドレスを確認

認証情報ファイルから確認：
```bash
cat ~/Downloads/eventdatamanager-479423-4f50df8b60ce.json | grep client_email
```

出力例：
```
"client_email": "your-service-account@eventdatamanager-479423.iam.gserviceaccount.com"
```

### 4. スプレッドシートに権限を付与

1. 対象の Google スプレッドシートを開く
2. 右上の「共有」ボタンをクリック
3. サービスアカウントのメールアドレスを入力
4. 権限を「編集者」に設定
5. 「送信」をクリック（通知は不要）

### 5. スクリプトを実行

API 有効化後、数分待ってから再実行：

```bash
# 仮想環境を有効化
source csv_to_sheets_env/bin/activate

# スクリプトを実行
python csv_to_sheets.py \
  sample/event_306730_participants.csv \
  "1Rv_V1jEe8DUMxAk_94bl7TqZa6lRVR5qCgoMx9GKHnU" \
  --sheet "シート1" \
  -c ~/Downloads/eventdatamanager-479423-4f50df8b60ce.json \
  --no-clear
```

## トラブルシューティング

### エラー: "Google Sheets API has not been used"

- **原因**: API が有効化されていない
- **解決**: 上記手順1を実行

### エラー: "PermissionError" または "SpreadsheetNotFound"

- **原因**: サービスアカウントに権限がない
- **解決**: 上記手順4を実行

### エラー: "ModuleNotFoundError: No module named 'pandas'"

- **原因**: 仮想環境が有効化されていない
- **解決**: `source csv_to_sheets_env/bin/activate` を実行

## 必要な API

このスクリプトは以下の Google API を使用します：

- ✅ **Google Sheets API**: スプレッドシートの読み書き
- ✅ **Google Drive API**: スプレッドシートへのアクセス

両方とも Google Cloud プロジェクトで有効化する必要があります。

## セキュリティ注意事項

- サービスアカウントの認証情報（JSON ファイル）は機密情報です
- Git リポジトリにコミットしないでください
- 必要最小限の権限のみを付与してください
