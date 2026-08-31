"""
日本語TTS発音補正辞書モジュール (Pronunciation Dictionary)

【設計方針】
- themes.py のナレーション原稿（Single Source of Truth / 画面字幕表示用）は自然な漢字表記のまま維持する。
- edge-tts（Microsoft Neural TTS）へ渡す直前に本モジュールの発音補正を適用し、文脈依存の誤読（例: 「〜たい方へ」->「ほうへ」）を確実に防止する。
- 「方法」「方向」「方針」等の正しい漢字表記に影響を与えないよう、単語・文脈単位の正規表現/フレーズマッチングで精密に置換する。
- 今後新たな読み間違いが発見された場合は、PRONUNCIATION_RULES リストにルールを追加するだけで安全に拡張可能。
"""

import re

# 発音補正ルールリスト
# 形式: (検索パターン[正規表現/文字列], 読み上げ用置換文字列, 補足説明)
PRONUNCIATION_RULES = [
    # 1. 「〜たい方へ」（動詞希望形 + 方へ）の誤読防止（ほうへ -> かたへ）
    (r"整えたい方へ", "整えたいかたへ", "theme_6_2: 整えたい方へ -> ととのえたいかたへ"),
    (r"歩きたい方へ", "歩きたいかたへ", "歩きたい方へ -> あるきたいかたへ"),
    (r"知りたい方へ", "知りたいかたへ", "知りたい方へ -> しりたいかたへ"),
    (r"相談したい方へ", "相談したいかたへ", "相談したい方へ -> そうだんしたいかたへ"),
]

def apply_pronunciation_dict(text: str) -> str:
    """
    ナレーション原文に対して発音補正辞書を適用し、TTS読み上げ用テキストを生成する。
    
    Args:
        text (str): ナレーション原文（画面字幕用）
    Returns:
        str: 発音補正済みテキスト（TTS音声生成用）
    """
    if not text:
        return ""
    
    corrected = text
    for rule in PRONUNCIATION_RULES:
        pattern, replacement = rule[0], rule[1]
        corrected = re.sub(pattern, replacement, corrected)
    
    return corrected

if __name__ == '__main__':
    # 動作検証用テスト
    test_cases = [
        ("ふらつきやすい姿勢を整えたい方へ。", "ふらつきやすい姿勢を整えたいかたへ。"),
        ("この方法でリハビリを行います。", "この方法でリハビリを行います。"),
        ("正しい方向へ体を動かします。", "正しい方向へ体を動かします。"),
        ("西田医院の治療方針です。", "西田医院の治療方針です。"),
        ("いつまでも元気に歩きたい方へ。", "いつまでも元気に歩きたいかたへ。")
    ]
    
    print("=== Pronunciation Dictionary Test ===")
    all_ok = True
    for original, expected in test_cases:
        actual = apply_pronunciation_dict(original)
        passed = (actual == expected)
        if not passed:
            all_ok = False
        print(f"[{'PASS' if passed else 'FAIL'}]")
        print(f"  Input:    {original}")
        print(f"  Expected: {expected}")
        print(f"  Actual:   {actual}")
    
    print(f"\nAll tests passed: {all_ok}")
