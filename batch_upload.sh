#!/bin/bash

#############################################################################
# CSV一括アップロードスクリプト
#
# 説明: csv_files/ ディレクトリ内の全CSVファイルをGoogleスプレッドシートに
#       一括アップロードします。各CSVファイル名がシート名として使用されます。
#
# 使用方法:
#   ./batch_upload.sh
#
# 設定:
#   スプレッドシートIDと認証情報はスクリプト内で設定してください（下記の設定セクション）
#
#############################################################################

# ============================================================================
# 設定セクション - ここを編集してください
# ============================================================================

# GoogleスプレッドシートID
# URLの場合: https://docs.google.com/spreadsheets/d/{この部分がID}/edit
SPREADSHEET_ID="1Rv_V1jEe8DUMxAk_94bl7TqZa6lRVR5qCgoMx9GKHnU"

# Google認証情報ファイルのパス
CREDENTIALS="credentials.json"
# または絶対パス: CREDENTIALS="$HOME/Downloads/eventdatamanager-479423-4f50df8b60ce.json"

# GAS（Google Apps Script）実行設定（オプション）
# CSVアップロード後にGASスクリプトを自動実行する場合は以下を設定
EXECUTE_GAS=false  # trueに設定するとGASを実行
GAS_SCRIPT_ID=""   # GASプロジェクトのScript ID（例: AKfycbyXXXXXXXXXXXXX）
GAS_FUNCTION=""    # 実行する関数名（例: onDataUploaded）
GAS_PARAMS=""      # 関数に渡すパラメータ（JSON配列形式、例: '["arg1", 123]'）

# ============================================================================
# システム設定（通常は変更不要）
# ============================================================================

# カラー出力用の定義
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 基本設定
CSV_DIR="csv_files"
PYTHON_SCRIPT="csv_to_sheets.py"
PYTHON_CMD="csv_to_sheets_env/bin/python"

# スクリプトのディレクトリに移動
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# ============================================================================
# 前提条件チェック
# ============================================================================

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}CSV一括アップロードスクリプト${NC}"
echo -e "${BLUE}==================================================${NC}"
echo ""

# 設定値の確認
if [ -z "$SPREADSHEET_ID" ]; then
    echo -e "${RED}エラー: SPREADSHEET_ID が設定されていません${NC}"
    echo -e "${YELLOW}スクリプト内の設定セクションでSPREADSHEET_IDを設定してください${NC}"
    exit 1
fi

if [ -z "$CREDENTIALS" ]; then
    echo -e "${RED}エラー: CREDENTIALS が設定されていません${NC}"
    echo -e "${YELLOW}スクリプト内の設定セクションでCREDENTIALSを設定してください${NC}"
    exit 1
fi

# Pythonスクリプトの存在確認
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${RED}エラー: $PYTHON_SCRIPT が見つかりません${NC}"
    exit 1
fi

# Python環境の確認
if [ ! -f "$PYTHON_CMD" ]; then
    echo -e "${RED}エラー: Python仮想環境が見つかりません${NC}"
    echo -e "${YELLOW}ヒント: 先に仮想環境を作成してください${NC}"
    echo "  python3 -m venv csv_to_sheets_env"
    echo "  source csv_to_sheets_env/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# CSVディレクトリの存在確認
if [ ! -d "$CSV_DIR" ]; then
    echo -e "${RED}エラー: $CSV_DIR ディレクトリが見つかりません${NC}"
    exit 1
fi

# 認証情報ファイルの確認
if [ ! -f "$CREDENTIALS" ]; then
    echo -e "${RED}エラー: 認証情報ファイル $CREDENTIALS が見つかりません${NC}"
    echo -e "${YELLOW}ヒント: スクリプト内の設定セクションでCREDENTIALSのパスを確認してください${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Pythonスクリプト: $PYTHON_SCRIPT"
echo -e "${GREEN}✓${NC} Python環境: $PYTHON_CMD"
echo -e "${GREEN}✓${NC} CSVディレクトリ: $CSV_DIR"
echo -e "${GREEN}✓${NC} 認証情報: $CREDENTIALS"
echo -e "${GREEN}✓${NC} スプレッドシートID: $SPREADSHEET_ID"
echo ""

# CSVファイルの検索
CSV_FILES=()
while IFS= read -r -d '' file; do
    CSV_FILES+=("$file")
done < <(find "$CSV_DIR" -name "*.csv" -type f -print0)

if [ ${#CSV_FILES[@]} -eq 0 ]; then
    echo -e "${RED}エラー: $CSV_DIR 内にCSVファイルが見つかりません${NC}"
    exit 1
fi

echo -e "${BLUE}検出されたCSVファイル: ${#CSV_FILES[@]}個${NC}"
for csv_file in "${CSV_FILES[@]}"; do
    echo "  - $csv_file"
done
echo ""

# 確認プロンプト
echo -e "${YELLOW}上記のCSVファイルをスプレッドシートにアップロードします。${NC}"
echo -e "${YELLOW}続行しますか? (y/N):${NC} "
read -r confirmation

if [[ ! "$confirmation" =~ ^[Yy]$ ]]; then
    echo -e "${RED}キャンセルされました${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}アップロード開始${NC}"
echo -e "${BLUE}==================================================${NC}"
echo ""

# カウンター
SUCCESS_COUNT=0
FAILURE_COUNT=0
FAILED_FILES=()

# 各CSVファイルを処理
for csv_file in "${CSV_FILES[@]}"; do
    # ファイル名からシート名を生成（拡張子を除く）
    filename=$(basename "$csv_file")
    sheet_name="${filename%.csv}"

    echo -e "${BLUE}------------------------------------------------${NC}"
    echo -e "${BLUE}処理中: $filename${NC}"
    echo -e "  シート名: ${YELLOW}$sheet_name${NC}"
    echo ""

    # Pythonスクリプトを実行
    if "$PYTHON_CMD" "$PYTHON_SCRIPT" \
        "$csv_file" \
        "$SPREADSHEET_ID" \
        --sheet "$sheet_name" \
        -c "$CREDENTIALS" \
        --no-clear; then

        echo ""
        echo -e "${GREEN}✓ 成功: $filename${NC}"
        ((SUCCESS_COUNT++))
    else
        echo ""
        echo -e "${RED}✗ 失敗: $filename${NC}"
        ((FAILURE_COUNT++))
        FAILED_FILES+=("$filename")
    fi
    echo ""
done

# 結果サマリー
echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}アップロード完了${NC}"
echo -e "${BLUE}==================================================${NC}"
echo ""
echo -e "総ファイル数: ${BLUE}${#CSV_FILES[@]}${NC}"
echo -e "成功: ${GREEN}$SUCCESS_COUNT${NC}"
echo -e "失敗: ${RED}$FAILURE_COUNT${NC}"
echo ""

if [ $FAILURE_COUNT -gt 0 ]; then
    echo -e "${RED}失敗したファイル:${NC}"
    for failed_file in "${FAILED_FILES[@]}"; do
        echo -e "  ${RED}✗${NC} $failed_file"
    done
    echo ""
    exit 1
else
    echo -e "${GREEN}すべてのファイルが正常にアップロードされました！${NC}"
    echo ""
    echo -e "スプレッドシートを確認:"
    echo -e "  ${BLUE}https://docs.google.com/spreadsheets/d/$SPREADSHEET_ID${NC}"
    echo ""

    # GAS実行処理（オプション）
    if [ "$EXECUTE_GAS" = true ]; then
        echo -e "${BLUE}==================================================${NC}"
        echo -e "${BLUE}Google Apps Script 実行${NC}"
        echo -e "${BLUE}==================================================${NC}"
        echo ""

        # GAS設定の検証
        if [ -z "$GAS_SCRIPT_ID" ]; then
            echo -e "${RED}エラー: GAS_SCRIPT_ID が設定されていません${NC}"
            echo -e "${YELLOW}スクリプト内の設定セクションでGAS_SCRIPT_IDを設定してください${NC}"
            exit 1
        fi

        if [ -z "$GAS_FUNCTION" ]; then
            echo -e "${RED}エラー: GAS_FUNCTION が設定されていません${NC}"
            echo -e "${YELLOW}スクリプト内の設定セクションでGAS_FUNCTIONを設定してください${NC}"
            exit 1
        fi

        # execute_gas.pyの存在確認
        GAS_EXECUTOR="execute_gas.py"
        if [ ! -f "$GAS_EXECUTOR" ]; then
            echo -e "${RED}エラー: $GAS_EXECUTOR が見つかりません${NC}"
            exit 1
        fi

        # GASスクリプトを実行
        echo -e "${BLUE}GASスクリプトを実行しています...${NC}"
        echo ""

        if [ -n "$GAS_PARAMS" ]; then
            # パラメータありで実行
            if "$PYTHON_CMD" "$GAS_EXECUTOR" \
                "$GAS_SCRIPT_ID" \
                "$GAS_FUNCTION" \
                -c "$CREDENTIALS" \
                --params "$GAS_PARAMS"; then
                echo ""
                echo -e "${GREEN}✓ GASスクリプトの実行が完了しました${NC}"
            else
                echo ""
                echo -e "${RED}✗ GASスクリプトの実行に失敗しました${NC}"
                exit 1
            fi
        else
            # パラメータなしで実行
            if "$PYTHON_CMD" "$GAS_EXECUTOR" \
                "$GAS_SCRIPT_ID" \
                "$GAS_FUNCTION" \
                -c "$CREDENTIALS"; then
                echo ""
                echo -e "${GREEN}✓ GASスクリプトの実行が完了しました${NC}"
            else
                echo ""
                echo -e "${RED}✗ GASスクリプトの実行に失敗しました${NC}"
                exit 1
            fi
        fi
        echo ""
    fi

    exit 0
fi
