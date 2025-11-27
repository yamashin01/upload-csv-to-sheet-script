#!/usr/bin/env python3
# 仮想環境を使用する場合は、以下のように絶対パスを指定することも可能:
# #!/Users/yamada/Documents/future_tech/dev/python-csv_to_sheets/csv_to_sheets_env/bin/python3

import sys
import argparse
import pandas as pd
import gspread
from pathlib import Path
from google.oauth2.service_account import Credentials

def load_credentials(credentials_path):
    """Google認証情報を読み込む"""
    # パスを正規化（日本語パス対応）
    credentials_path = Path(credentials_path).expanduser().resolve()

    if not credentials_path.exists():
        print(f"エラー: {credentials_path} が見つかりません")
        sys.exit(1)

    scope = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = Credentials.from_service_account_file(str(credentials_path), scopes=scope)
    return creds

def read_csv(csv_path):
    """CSVファイルを読み込む（日本語パス対応）"""
    # パスを正規化（~展開、絶対パス化、日本語パス対応）
    csv_path = Path(csv_path).expanduser().resolve()

    if not csv_path.exists():
        print(f"エラー: {csv_path} が見つかりません")
        sys.exit(1)

    # エンコーディングと区切り文字を自動検出して読み込む
    encodings = ['utf-8', 'utf-8-sig', 'utf-16', 'utf-16-le', 'utf-16-be', 'cp932', 'shift_jis']
    separators = [',', '\t']  # カンマ区切りとタブ区切り

    for encoding in encodings:
        for sep in separators:
            try:
                df = pd.read_csv(str(csv_path), encoding=encoding, sep=sep)
                # 正常に読み込めたことを確認（列数が1より大きい）
                if len(df.columns) > 1:
                    sep_name = 'タブ' if sep == '\t' else 'カンマ'
                    print(f"  検出されたエンコーディング: {encoding}")
                    print(f"  検出された区切り文字: {sep_name}")
                    return df
            except (UnicodeDecodeError, UnicodeError, pd.errors.ParserError):
                continue

    # 全てのエンコーディングで失敗した場合
    print(f"エラー: ファイルのエンコーディングまたは形式を自動検出できませんでした")
    print(f"サポートされているエンコーディング: {', '.join(encodings)}")
    print(f"サポートされている区切り文字: カンマ(,), タブ(\\t)")
    sys.exit(1)

def extract_spreadsheet_id(spreadsheet_input):
    """URLまたはIDからスプレッドシートIDを抽出"""
    if spreadsheet_input.startswith('https://'):
        # URLの場合、IDを抽出
        # https://docs.google.com/spreadsheets/d/{ID}/edit...
        import re
        match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', spreadsheet_input)
        if match:
            return match.group(1)
        else:
            print("エラー: 無効なGoogleスプレッドシートのURLです")
            sys.exit(1)
    else:
        # IDとして直接使用
        return spreadsheet_input

def write_to_spreadsheet(df, spreadsheet_id, sheet_name, credentials_path, clear_sheet=True):
    """スプレッドシートにデータを書き込む"""
    creds = load_credentials(credentials_path)
    client = gspread.authorize(creds)
    
    try:
        spreadsheet = client.open_by_key(spreadsheet_id)
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"エラー: スプレッドシートID '{spreadsheet_id}' が見つかりません")
        print("以下の方法でIDを確認してください:")
        print("  1. Googleドライブでスプレッドシートを開く")
        print("  2. URLから以下の部分をコピー: https://docs.google.com/spreadsheets/d/{ID}/edit...")
        sys.exit(1)
    
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        print(f"情報: シート '{sheet_name}' が見つかりません。新規作成します")
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1, cols=1)
    
    # シートをクリア（オプション）
    if clear_sheet:
        worksheet.clear()
    
    # NaN値を空文字列に置換（JSON互換性のため）
    df = df.fillna('')

    # ヘッダーとデータを一括で準備
    header = df.columns.tolist()
    data_rows = df.values.tolist()

    # 全データを一括で書き込み（パフォーマンス向上）
    all_data = [header] + data_rows
    worksheet.update('A1', all_data, value_input_option='RAW')
    
    print(f"✓ {len(data_rows)} 行のデータをスプレッドシートに書き込みました")
    print(f"  スプレッドシートID: {spreadsheet_id}")
    print(f"  シート: {sheet_name}")

def main():
    parser = argparse.ArgumentParser(
        description='CSVファイルをGoogleスプレッドシートに出力します'
    )
    parser.add_argument(
        'csv_path',
        help='CSVファイルのパス'
    )
    parser.add_argument(
        'spreadsheet_id',
        help='Googleスプレッドシートの共有URL、またはスプレッドシートID'
    )
    parser.add_argument(
        '-s', '--sheet',
        default='Sheet1',
        help='シート名（デフォルト: Sheet1）'
    )
    parser.add_argument(
        '-c', '--credentials',
        default='credentials.json',
        help='Google認証情報ファイル（デフォルト: credentials.json）'
    )
    parser.add_argument(
        '--no-clear',
        action='store_true',
        help='既存データをクリアせず追記する'
    )
    parser.add_argument(
        '-d', '--dry-run',
        action='store_true',
        help='ドライラン: 実際には書き込まず、プレビューのみ表示'
    )
    
    args = parser.parse_args()
    
    # スプレッドシートIDを抽出（URLまたはIDから）
    spreadsheet_id = extract_spreadsheet_id(args.spreadsheet_id)
    
    # CSVを読み込む
    print(f"CSVファイルを読み込んでいます: {args.csv_path}")
    df = read_csv(args.csv_path)
    print(f"✓ {len(df)} 行、{len(df.columns)} 列のデータを読み込みました")
    
    # プレビュー表示
    print("\nデータプレビュー:")
    print(df.head())
    print(f"\nカラム: {', '.join(df.columns.tolist())}")
    
    if args.dry_run:
        print("\n[ドライラン] 実際には書き込みません")
        return
    
    # スプレッドシートに書き込む
    print("\nスプレッドシートに書き込んでいます...")
    write_to_spreadsheet(
        df,
        spreadsheet_id,
        args.sheet,
        args.credentials,
        clear_sheet=not args.no_clear
    )
    print("完了しました！")

if __name__ == '__main__':
    main()