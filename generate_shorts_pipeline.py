import os
import sys
import json
from voice_generator import generate_voice_with_timeline, generate_voice
from shorts_editor import build_shorts_video
from themes import DEFAULT_THEME, get_theme_by_id, get_all_themes, select_next_theme, select_random_test_theme, commit_theme_state

try:
    import budoux
    _budoux_parser = budoux.load_default_japanese_parser()
except Exception:
    _budoux_parser = None

INPUT_VIDEO = os.environ.get('INPUT_VIDEO', os.path.join('test_output', 'shorts_test.mp4'))
OUTPUT_VIDEO = os.environ.get('OUTPUT_VIDEO', os.path.join('test_output', 'tts_video_test.mp4'))
NARRATION_PATH = os.path.join('test_output', 'narration.mp3')
CURRENT_THEME_JSON = os.path.join('test_output', 'current_theme.json')
PRESET_BG_PATH = os.path.join('assets', 'videos', 'default_medical_bg.mp4')

def format_text_to_lines(text, max_line_len=14):
    """
    BudouX（日本語形態素・文脈分節解析）を活用し、
    意味のまとまり（単語・文脈の区切り）を崩さずに
    行ごとの文字数バランスが最も美しくなるよう適切に改行する
    """
    text = text.strip()
    if len(text) <= 12:
        return [text]

    # BudouX による文脈チャンク分割
    if _budoux_parser:
        chunks = _budoux_parser.parse(text)
    else:
        chunks = [text]

    n = len(chunks)
    if n <= 1:
        if '、' in text:
            parts = text.split('、', 1)
            return [parts[0] + '、', parts[1]]
        mid = len(text) // 2
        return [text[:mid], text[mid:]]

    # 1. 2行分割の最適バランス探索（各行が max_line_len+1 以内で文字数差が最小）
    best_2lines = None
    min_diff_2 = float('inf')
    for i in range(1, n):
        l1 = "".join(chunks[:i])
        l2 = "".join(chunks[i:])
        if len(l1) <= max_line_len + 1 and len(l2) <= max_line_len + 1:
            diff = abs(len(l1) - len(l2))
            if diff < min_diff_2:
                min_diff_2 = diff
                best_2lines = [l1, l2]

    if best_2lines is not None and min_diff_2 <= 6:
        return best_2lines

    # 2. 3行分割の最適バランス探索（長文用：各行が max_line_len 以内で文字数差が最小）
    best_3lines = None
    min_diff_3 = float('inf')
    for i in range(1, n - 1):
        for j in range(i + 1, n):
            l1 = "".join(chunks[:i])
            l2 = "".join(chunks[i:j])
            l3 = "".join(chunks[j:])
            if len(l1) <= max_line_len and len(l2) <= max_line_len and len(l3) <= max_line_len:
                diff = max(len(l1), len(l2), len(l3)) - min(len(l1), len(l2), len(l3))
                if diff < min_diff_3:
                    min_diff_3 = diff
                    best_3lines = [l1, l2, l3]

    if best_3lines is not None:
        return best_3lines

    # 3. 貪欲法フォールバック
    lines = []
    curr = ""
    for c in chunks:
        if len(curr + c) <= max_line_len:
            curr += c
        else:
            if curr:
                lines.append(curr)
            curr = c
    if curr:
        lines.append(curr)
    return lines

def build_dynamic_scenes_from_timeline(sentences, total_video_duration=15.0):
    """
    TTSの実際の文単位タイムスタンプから、音声と100%同期する字幕シーンを動的生成
    """
    dynamic_scenes = []
    num_sentences = len(sentences)

    for i, s in enumerate(sentences):
        sentence_text = s["text"]
        start_t = s["start"]
        end_t = s["end"]

        # シーン1の開始は動画の頭(0.0秒)から先行表示して視認性を確保
        if i == 0:
            scene_start = 0.0
        else:
            scene_start = start_t

        # 最後のシーン（CTA文）は動画終了(15.0秒)まで表示を継続
        if i == num_sentences - 1:
            scene_end = total_video_duration
        else:
            # 次の文が始まる直前まで表示を維持してチラつきを防止
            next_start = sentences[i + 1]["start"]
            scene_end = round(max(end_t, next_start), 2)

        # BudouX を用いた美しい文脈・形態素バランシング改行
        lines = format_text_to_lines(sentence_text, max_line_len=14)

        dynamic_scenes.append({
            "start": scene_start,
            "end": scene_end,
            "speech_start": start_t,
            "speech_end": end_t,
            "lines": lines
        })

    return dynamic_scenes

def run_pipeline(theme=None, input_video=None, output_video=None, mode=None):
    if input_video is None:
        input_video = INPUT_VIDEO
    if output_video is None:
        output_video = OUTPUT_VIDEO

    # 背景動画の安全なフォールバック
    if not os.path.exists(input_video):
        print(f"[PIPELINE WARNING] Input video '{input_video}' not found. Falling back to preset: '{PRESET_BG_PATH}'")
        if os.path.exists(PRESET_BG_PATH):
            input_video = PRESET_BG_PATH
        else:
            print(f"[PIPELINE ERROR] Preset background video not found at '{PRESET_BG_PATH}'", file=sys.stderr)
            sys.exit(1)

    # テーマ選択：モード判定（テスト用シャッフルプール vs 本番日次ローテーション）
    if theme is None:
        mode_env = os.environ.get('THEME_MODE', '').strip().upper()
        if mode == 'random' or mode == 'test' or mode_env in ['RANDOM', 'TEST']:
            theme = select_random_test_theme()
        else:
            theme = select_next_theme()

    narration_text = theme.get('narration', '').strip()
    print("=== YouTube Shorts Generation Pipeline ===")
    print(f"Theme ID: {theme.get('theme_id')}")
    print(f"Theme Category: {theme.get('category')}")
    print(f"Theme Title: {theme.get('title')}")
    print(f"Hook Type: {theme.get('hook_type', 'SURPRISE')}")
    print(f"Structure: {theme.get('structure_type', 'HOOK → EXPLANATION → CTA')}")
    print(f"Angle: {theme.get('angle', '')}")
    print(f"Narration Master Text (Single Source of Truth): \"{narration_text}\"")

    # 1. TTS音声生成＆文単位タイムスタンプの取得
    tts_success, sentence_timeline = generate_voice_with_timeline(
        text=narration_text,
        output_path=NARRATION_PATH,
        voice_config={'voice': 'ja-JP-NanamiNeural', 'rate': '-5%'}
    )

    if tts_success and sentence_timeline:
        print("[PIPELINE] TTS generation SUCCESS. Building synchronized dynamic scenes.")
        dynamic_scenes = build_dynamic_scenes_from_timeline(sentence_timeline, total_video_duration=15.0)
        theme['scenes'] = dynamic_scenes

        # [VIDEO VARIATION] ログ出力（指示要件準拠）
        print("\n[VIDEO VARIATION]")
        print(f"Theme: {theme.get('theme_id')} ({theme.get('title')})")
        print(f"Hook: {theme.get('hook_type', 'SURPRISE')}")
        print(f"Structure: {theme.get('structure_type', 'HOOK → EXPLANATION → CTA')}")
        print(f"Angle: {theme.get('angle', '')}")
        print(f"Background strategy: THEME_BASED ('{theme.get('bg_query')}')")
        print(f"CTA: {theme.get('cta', '詳しくはプロフィールへ。')}")
        print(f"Narration: \"{narration_text}\"")
        for idx, sc in enumerate(dynamic_scenes):
            print(f"Scene {idx + 1}:")
            print(f"  start={sc['start']:.2f}")
            print(f"  end={sc['end']:.2f}")
            print(f"  text={' / '.join(sc['lines'])}")
        print(f"Audio duration: {sentence_timeline[-1]['end']:.2f}s")
        print(f"Video duration: 15.00s\n")

    else:
        print("[PIPELINE] [FALLBACK ACTIVE] TTS generation FAILED. Using existing scene fallback.")
        if os.path.exists(NARRATION_PATH):
            os.remove(NARRATION_PATH)

    # 現在テーマ情報を一時保存
    os.makedirs(os.path.dirname(os.path.abspath(CURRENT_THEME_JSON)), exist_ok=True)
    with open(CURRENT_THEME_JSON, 'w', encoding='utf-8') as f:
        json.dump(theme, f, ensure_ascii=False, indent=2)

    # 2. 動画合成レンダリング
    build_shorts_video(
        input_video=input_video,
        output_video=output_video,
        theme=theme,
        narration_path=NARRATION_PATH if tts_success else None
    )

    print("=== Pipeline Execution Complete ===")
    return theme

if __name__ == '__main__':
    run_pipeline()
