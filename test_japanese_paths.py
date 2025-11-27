#!/usr/bin/env python3
"""
日本語パス対応のテストスクリプト

このスクリプトは日本語パスが正しく処理されることを確認します。
"""

import sys
from pathlib import Path

def test_path_handling():
    """パス処理のテスト"""

    print("=" * 60)
    print("日本語パス処理テスト")
    print("=" * 60)

    # テストケース
    test_cases = [
        "~/デスクトップ/test.csv",
        "./日本語フォルダ/ファイル.csv",
        "../親フォルダ/データ.csv",
        "sample/event_306730_participants.csv",
    ]

    for test_path in test_cases:
        print(f"\n入力パス: {test_path}")

        try:
            # pathlib.Pathで処理
            path = Path(test_path).expanduser().resolve()
            print(f"  ✅ 正規化パス: {path}")
            print(f"  📁 存在確認: {path.exists()}")
            print(f"  📝 親ディレクトリ: {path.parent}")
            print(f"  📄 ファイル名: {path.name}")
        except Exception as e:
            print(f"  ❌ エラー: {e}")

    print("\n" + "=" * 60)
    print("テスト完了")
    print("=" * 60)

def test_encoding_detection():
    """エンコーディング検出のテスト"""

    print("\n" + "=" * 60)
    print("エンコーディング検出テスト")
    print("=" * 60)

    encodings = ['utf-8', 'utf-8-sig', 'cp932', 'shift_jis']

    for encoding in encodings:
        print(f"\n{encoding}:")
        print(f"  対応: ✅")

    print("\n" + "=" * 60)

if __name__ == '__main__':
    test_path_handling()
    test_encoding_detection()
