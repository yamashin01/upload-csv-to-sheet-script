# Google Apps Script (GAS) 自動実行ガイド

このガイドでは、CSVアップロード後にGoogleスプレッドシートに紐付けられたGASスクリプトを自動実行する方法を説明します。

---

## 📋 目次

1. [前提条件](#前提条件)
2. [GASスクリプトの準備](#gasスクリプトの準備)
3. [認証情報の設定](#認証情報の設定)
4. [batch_upload.shの設定](#batch_uploadshの設定)
5. [使用方法](#使用方法)
6. [トラブルシューティング](#トラブルシューティング)

---

## 🎯 前提条件

1. ✅ Python仮想環境が設定済み
2. ✅ `credentials.json` (サービスアカウント認証情報) が配置済み
3. ✅ Googleスプレッドシートが作成済み
4. ✅ Apps Script APIが有効

### 必要なPythonライブラリ

```bash
# 新しい依存関係をインストール
source csv_to_sheets_env/bin/activate
pip install -r requirements.txt
```

**追加されたライブラリ**:
- `google-api-python-client>=2.0.0`

---

## 📝 GASスクリプトの準備

### Step 1: GASプロジェクトを作成

1. Googleスプレッドシートを開く
2. **「拡張機能」** → **「Apps Script」** をクリック
3. スクリプトエディタが開きます

### Step 2: 実行したい関数を作成

例: データアップロード後に通知メールを送信する関数

```javascript
/**
 * データアップロード後に実行される関数
 *
 * @param {string} sheetName - アップロードされたシート名
 * @param {number} rowCount - アップロードされた行数
 */
function onDataUploaded(sheetName, rowCount) {
  // スプレッドシートを取得
  var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = spreadsheet.getSheetByName(sheetName);

  // ログ出力
  Logger.log('データがアップロードされました');
  Logger.log('シート名: ' + sheetName);
  Logger.log('行数: ' + rowCount);

  // メール通知（オプション）
  var email = Session.getActiveUser().getEmail();
  var subject = 'データアップロード完了通知';
  var body = 'シート "' + sheetName + '" に ' + rowCount + ' 行のデータがアップロードされました。';

  MailApp.sendEmail(email, subject, body);

  return {
    success: true,
    message: '処理が完了しました'
  };
}

/**
 * パラメータなしで実行される関数の例
 */
function processAllData() {
  var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  var sheets = spreadsheet.getSheets();

  Logger.log('全シートを処理します: ' + sheets.length + ' シート');

  sheets.forEach(function(sheet) {
    var lastRow = sheet.getLastRow();
    Logger.log('シート: ' + sheet.getName() + ', 行数: ' + lastRow);
  });

  return {
    success: true,
    processedSheets: sheets.length
  };
}
```

### Step 3: Script IDを取得

1. スクリプトエディタで **「プロジェクトの設定」**（歯車アイコン）をクリック
2. **「IDs」** セクションの **「Script ID」** をコピー
   - 例: `AKfycbyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`

### Step 4: デプロイメント（重要！）

GASスクリプトを外部から実行するには、デプロイが必要です：

1. スクリプトエディタで **「デプロイ」** → **「新しいデプロイ」** をクリック
2. **「種類の選択」** → **「API 実行可能ファイル」** を選択
3. **「次のユーザーとして実行」**: 「自分」を選択
4. **「アクセスできるユーザー」**: 「全員」または適切な権限を選択
5. **「デプロイ」** をクリック
6. デプロイIDが表示されます（これがScript IDです）

---

## 🔐 認証情報の設定

### Apps Script APIを有効化

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. サービスアカウントを使用しているプロジェクトを選択
3. **「APIとサービス」** → **「ライブラリ」** に移動
4. **「Google Apps Script API」** を検索して有効化

### サービスアカウントに権限を付与

GASプロジェクトで、サービスアカウントに実行権限を付与する必要があります：

**方法1: スプレッドシートの共有**
1. スプレッドシートの **「共有」** をクリック
2. サービスアカウントのメールアドレスを追加（`*****@*****.iam.gserviceaccount.com`）
3. 権限を **「編集者」** に設定

**方法2: GASプロジェクトのマニフェストで設定**
1. スクリプトエディタで `appsscript.json` を開く（表示されていない場合は、設定で「マニフェストファイルをエディタで表示する」を有効化）
2. 以下のスコープを追加：

```json
{
  "timeZone": "Asia/Tokyo",
  "dependencies": {},
  "exceptionLogging": "STACKDRIVER",
  "oauthScopes": [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/script.external_request"
  ],
  "runtimeVersion": "V8"
}
```

---

## ⚙️ batch_upload.shの設定

`batch_upload.sh` の設定セクションを編集します：

```bash
# GAS（Google Apps Script）実行設定（オプション）
# CSVアップロード後にGASスクリプトを自動実行する場合は以下を設定
EXECUTE_GAS=true  # trueに設定するとGASを実行
GAS_SCRIPT_ID="AKfycbyXXXXXXXXXXXXXXXXXXXXXXXX"  # 取得したScript ID
GAS_FUNCTION="onDataUploaded"  # 実行する関数名
GAS_PARAMS='["Sheet1", 100]'  # 関数に渡すパラメータ（JSON配列）
```

### パラメータの形式

- **パラメータなし**: `GAS_PARAMS=""`
- **パラメータあり**: JSON配列形式で指定
  ```bash
  GAS_PARAMS='["文字列", 123, true]'  # 文字列、数値、真偽値
  GAS_PARAMS='["Sheet1"]'  # 単一パラメータ
  ```

---

## 🚀 使用方法

### 基本的な使い方

```bash
# batch_upload.shを実行
./batch_upload.sh
```

実行フロー：
1. CSV ファイルを Googleスプレッドシートにアップロード
2. すべてのCSVファイルのアップロードが完了
3. **GASスクリプトが自動実行される**（`EXECUTE_GAS=true`の場合）

### 手動でGASスクリプトを実行

`execute_gas.py` を直接使用することもできます：

```bash
# 基本的な使い方
./execute_gas.py <SCRIPT_ID> <FUNCTION_NAME> -c credentials.json

# パラメータなしで実行
./execute_gas.py AKfycbyXXXXXXXXXXXXX processAllData -c credentials.json

# パラメータありで実行
./execute_gas.py AKfycbyXXXXXXXXXXXXX onDataUploaded \
  -c credentials.json \
  --params '["Sheet1", 100]'
```

---

## 🔧 トラブルシューティング

### 問題1: "API呼び出しエラー: 403 Forbidden"

**原因**: Apps Script APIが有効化されていない、または権限不足

**解決方法**:
1. [Google Cloud Console](https://console.cloud.google.com/) で Apps Script API を有効化
2. サービスアカウントにスプレッドシートへの編集権限を付与
3. GASプロジェクトがデプロイされているか確認

### 問題2: "Script ID が間違っている"

**原因**: Script IDの取得方法が間違っている

**解決方法**:
1. GASエディタで **「プロジェクトの設定」** を開く
2. **「IDs」** セクションの **「Script ID」** をコピー
3. デプロイメントIDではなく、Script IDを使用

### 問題3: "関数が見つからない"

**原因**: 指定した関数名が存在しない、またはデプロイされていない

**解決方法**:
1. GASエディタで関数名を確認
2. 関数がデプロイされているか確認（「デプロイ」→「デプロイを管理」）

### 問題4: "パラメータのJSON解析に失敗"

**原因**: `GAS_PARAMS` の形式が正しくない

**解決方法**:
- JSON配列形式で指定: `'["arg1", 123]'`
- シングルクォートで囲む
- 正しいJSON形式を確認

### 問題5: "google-api-python-client がインストールされていない"

**原因**: 依存ライブラリが不足

**解決方法**:
```bash
source csv_to_sheets_env/bin/activate
pip install -r requirements.txt
```

---

## 📚 参考資料

- [Google Apps Script API](https://developers.google.com/apps-script/api)
- [Apps Script API Quickstart](https://developers.google.com/apps-script/api/quickstart/python)
- [Service Account Authentication](https://developers.google.com/identity/protocols/oauth2/service-account)

---

## ✅ チェックリスト

実装前に以下を確認してください：

- [ ] Python仮想環境が作成済み
- [ ] `requirements.txt` から全てのライブラリをインストール済み
- [ ] サービスアカウント認証情報 (`credentials.json`) が配置済み
- [ ] GASスクリプトが作成済み
- [ ] GASプロジェクトがデプロイ済み
- [ ] Script IDを取得済み
- [ ] Apps Script APIが有効化済み
- [ ] サービスアカウントにスプレッドシート編集権限を付与済み
- [ ] `batch_upload.sh` の設定セクションを編集済み
- [ ] `execute_gas.py` に実行権限を付与済み (`chmod +x execute_gas.py`)

すべてチェックできたら、`./batch_upload.sh` を実行してください！
