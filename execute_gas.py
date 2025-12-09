#!/usr/bin/env python3
"""
Google Apps Script (GAS) 実行スクリプト

説明: Googleスプレッドシートに紐付いたGASスクリプトを外部から実行します。
Apps Script API を使用して、指定された関数を実行します。

使用方法:
  ./execute_gas.py <script_id> <function_name> [--credentials <path>] [--params <json>]

例:
  # 引数なしで実行
  ./execute_gas.py AKfycbyXXXXXXXXXXXXX myFunction -c credentials.json

  # 引数ありで実行
  ./execute_gas.py AKfycbyXXXXXXXXXXXXX processData -c credentials.json --params '["arg1", 123]'
"""

import sys
import argparse
import json
from pathlib import Path
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def load_credentials(credentials_path):
    """Google認証情報を読み込む（Apps Script API用）"""
    credentials_path = Path(credentials_path).expanduser().resolve()

    if not credentials_path.exists():
        print(f"エラー: {credentials_path} が見つかりません")
        sys.exit(1)

    # Apps Script API実行に必要なスコープ
    scopes = [
        'https://www.googleapis.com/auth/script.projects',
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    creds = Credentials.from_service_account_file(
        str(credentials_path),
        scopes=scopes
    )
    return creds


def execute_gas_function(script_id, function_name, credentials_path, parameters=None):
    """
    Apps Script API経由でGAS関数を実行

    Args:
        script_id: GASプロジェクトのScript ID (デプロイメントID)
        function_name: 実行する関数名
        credentials_path: 認証情報ファイルのパス
        parameters: 関数に渡すパラメータのリスト

    Returns:
        実行結果
    """
    try:
        # 認証情報を読み込む
        creds = load_credentials(credentials_path)

        # Apps Script APIクライアントを構築
        service = build('script', 'v1', credentials=creds)

        # 実行リクエストを構築
        request_body = {
            'function': function_name
        }

        if parameters:
            request_body['parameters'] = parameters

        print(f"GASスクリプトを実行しています...")
        print(f"  Script ID: {script_id}")
        print(f"  関数名: {function_name}")
        if parameters:
            print(f"  パラメータ: {parameters}")
        print()

        # Apps Script APIを呼び出して関数を実行
        response = service.scripts().run(
            scriptId=script_id,
            body=request_body
        ).execute()

        # 実行結果を処理
        if 'error' in response:
            error = response['error']
            error_message = error.get('details', [{}])[0].get('errorMessage', 'Unknown error')
            print(f"❌ GAS実行エラー: {error_message}")
            print(f"エラー詳細: {json.dumps(error, indent=2, ensure_ascii=False)}")
            return None

        # 成功した場合
        result = response.get('response', {}).get('result')
        print("✓ GASスクリプトの実行が完了しました")

        if result is not None:
            print(f"実行結果:")
            print(json.dumps(result, indent=2, ensure_ascii=False))

        return result

    except HttpError as e:
        print(f"❌ API呼び出しエラー: {e}")
        print("\n考えられる原因:")
        print("  1. Script IDが間違っている")
        print("  2. 認証情報にApps Script APIの権限がない")
        print("  3. GASプロジェクトがデプロイされていない")
        print("  4. サービスアカウントにスクリプト実行権限がない")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        sys.exit(1)


def get_script_id_from_spreadsheet(spreadsheet_id, credentials_path):
    """
    スプレッドシートIDからバインドされたGASのScript IDを取得

    注意: この機能は制限があります。多くの場合、Script IDは手動で確認する必要があります。

    Args:
        spreadsheet_id: GoogleスプレッドシートのID
        credentials_path: 認証情報ファイルのパス

    Returns:
        Script ID（取得できない場合はNone）
    """
    # 注: Google Sheets APIではバインドされたスクリプトのIDを直接取得できません
    # この情報はApps Script APIまたは手動で確認する必要があります
    print("⚠️  注意: Script IDはスプレッドシートから自動取得できません")
    print("   GASエディタから以下の方法でScript IDを取得してください:")
    print("   1. スプレッドシートで「拡張機能」→「Apps Script」を開く")
    print("   2. 「プロジェクトの設定」（歯車アイコン）をクリック")
    print("   3. 「IDs」セクションの「Script ID」をコピー")
    print()
    return None


def main():
    parser = argparse.ArgumentParser(
        description='Google Apps Script (GAS) の関数を外部から実行します'
    )
    parser.add_argument(
        'script_id',
        help='GASプロジェクトのScript ID (例: AKfycbyXXXXXXXXXXXXX)'
    )
    parser.add_argument(
        'function_name',
        help='実行する関数名 (例: myFunction)'
    )
    parser.add_argument(
        '-c', '--credentials',
        default='credentials.json',
        help='Google認証情報ファイル（デフォルト: credentials.json）'
    )
    parser.add_argument(
        '-p', '--params',
        default=None,
        help='関数に渡すパラメータ（JSON配列形式, 例: \'["arg1", 123]\'）'
    )
    parser.add_argument(
        '--spreadsheet-id',
        help='スプレッドシートIDから実行（Script IDの代わりに使用）'
    )

    args = parser.parse_args()

    # パラメータをパース
    parameters = None
    if args.params:
        try:
            parameters = json.loads(args.params)
            if not isinstance(parameters, list):
                print("エラー: --params は JSON配列形式で指定してください")
                print("例: --params '[\"arg1\", 123, true]'")
                sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"エラー: パラメータのJSON解析に失敗しました: {e}")
            sys.exit(1)

    # Script IDを取得
    script_id = args.script_id

    if args.spreadsheet_id:
        # スプレッドシートIDから取得を試みる（注: 制限あり）
        retrieved_id = get_script_id_from_spreadsheet(
            args.spreadsheet_id,
            args.credentials
        )
        if retrieved_id:
            script_id = retrieved_id
        else:
            print("エラー: Script IDを取得できませんでした")
            print("Script IDを直接指定してください")
            sys.exit(1)

    # GAS関数を実行
    execute_gas_function(
        script_id,
        args.function_name,
        args.credentials,
        parameters
    )


if __name__ == '__main__':
    main()
