import os
import sys
import json
import budoux
from voice_generator import generate_voice_with_timeline
from shorts_editor import build_shorts_video
from themes import select_next_theme, select_random_test_theme

# ディレクトリ・パス設定
OUTPUT_DIR = 'test_output'
NARRATION_PATH = os.path.join(OUTPUT_DIR, 'narration.mp3')
PRESET_BG_PATH = os.path.join('assets', 'preset_bg_short.mp4')
CURRENT_THEME_JSON = os.path.join(OUTPUT_DIR, 'current_theme.json')

INPUT_VIDEO = os.environ.get('INPUT_VIDEO', os.path.join(OUTPUT_DIR, 'shorts_test.mp4'))
OUTPUT_VIDEO = os.environ.get('OUTPUT_VIDEO', os.path.join(OUTPUT_DIR, 'shorts_final.mp4'))

# BudouX 日本語パーサー初期化（文脈・単語境界保持用）
try:
    _budoux_parser = budoux.load_default_japanese_parser()
except Exception as e:
    print(f"[PIPELINE WARNING] Failed to load BudouX parser: {e}", file=sys.stderr)
    _budoux_parser = None

def format_text_to_lines(text, max_line_len=14):
    """
    BudouX（日本語形態素・文脈分節解析）を活用し、
    一文字たりとも変更・省略・要約せず、
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

    # 3. 貪欲フォールバック（文字結合順序完全保証）
    lines = []
    curr = ""
    for ch in chunks:
        if len(curr) + len(ch) <= max_line_len:
            curr += ch
        else:
            if curr:
                lines.append(curr)
            curr = ch
    if curr:
        lines.append(curr)
    return lines

def build_dynamic_scenes_from_timeline(sentence_timeline, total_video_duration=15.0):
    """
    edge-ttsのSentenceBoundaryメタデータ（実音声タイムスタンプ）から、
    字幕重複（オーバーラップ）を0msに完全クランプし、
    ナレーションと完全同期する動的字幕シーンを構築する。
    """
    num_sentences = len(sentence_timeline)
    if num_sentences == 0:
        return []

    # 1. 各シーンの基準開始時刻を決定（最初の文は0.00s固定、以降は音声開始時刻）
    starts = []
    for i, s in enumerate(sentence_timeline):
        if i == 0:
            starts.append(0.0)
        else:
            starts.append(round(max(0.0, s['start']), 2))

    # 2. 前の終了時刻 ＝ 次の開始時刻 となるよう完全クランプ
    dynamic_scenes = []
    for i, s in enumerate(sentence_timeline):
        scene_start = starts[i]
        if i < num_sentences - 1:
            scene_end = starts[i + 1]
        else:
            scene_end = round(max(s['end'], float(total_video_duration)), 2)

        # 安全ガード：終了時刻が開始時刻以下にならないよう補正
        if scene_end <= scene_start:
            scene_end = round(scene_start + max(0.5, s.get('duration', 1.0)), 2)

        raw_text = s['text'].strip()
        balanced_lines = format_text_to_lines(raw_text)

        dynamic_scenes.append({
            'start': round(scene_start, 2),
            'end': round(scene_end, 2),
            'lines': balanced_lines,
            'raw_text': raw_text
        })

    # 3. 重複ゼロ（scene[i].end == scene[i+1].start）を完全保証
    for i in range(len(dynamic_scenes) - 1):
        dynamic_scenes[i]['end'] = dynamic_scenes[i + 1]['start']

    return dynamic_scenes

def build_fallback_scenes_from_narration(narration_text, total_video_duration=15.0):
    """
    TTSフォールバック時でも、ナレーション原稿（Single Source of Truth）を一文字一句変えずに
    句読点ベースで分割し、完全整列・重複ゼロの動的字幕シーンを構築する
    """
    import re
    raw_sentences = [s.strip() for s in re.split(r'([。！？!?])', narration_text) if s.strip()]
    merged_sentences = []
    for s in raw_sentences:
        if s in ['。', '！', '？', '!', '?'] and merged_sentences:
            merged_sentences[-1] += s
        else:
            merged_sentences.append(s)

    if not merged_sentences:
        merged_sentences = [narration_text]

    num_sentences = len(merged_sentences)
    duration_per_scene = float(total_video_duration) / max(1, num_sentences)

    dynamic_scenes = []
    for i, raw_text in enumerate(merged_sentences):
        scene_start = round(i * duration_per_scene, 2)
        scene_end = round(total_video_duration if i == num_sentences - 1 else (i + 1) * duration_per_scene, 2)
        balanced_lines = format_text_to_lines(raw_text)
        dynamic_scenes.append({
            'start': round(scene_start, 2),
            'end': round(scene_end, 2),
            'lines': balanced_lines,
            'raw_text': raw_text
        })

    for i in range(len(dynamic_scenes) - 1):
        dynamic_scenes[i]['end'] = dynamic_scenes[i + 1]['start']

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

    # テーマ選択：pexels_download.pyで保存された current_theme.json を最優先
    if theme is None:
        if os.path.exists(CURRENT_THEME_JSON):
            try:
                with open(CURRENT_THEME_JSON, 'r', encoding='utf-8') as f:
                    theme = json.load(f)
                    print(f"[PIPELINE SYNC] Loaded selected theme variation from {CURRENT_THEME_JSON}")
            except Exception as e:
                print(f"[PIPELINE WARNING] Failed to load {CURRENT_THEME_JSON}: {e}")
                theme = None

    if theme is None:
        mode_env = os.environ.get('THEME_MODE', '').strip().upper()
        if mode == 'random' or mode == 'test' or mode_env in ['RANDOM', 'TEST']:
            theme = select_random_test_theme()
        else:
            theme = select_next_theme()

    # Single Source of Truth: ナレーション原稿
    narration_text = theme.get('narration', '').strip()
    print("=== YouTube Shorts Generation Pipeline ===")
    print(f"Theme ID: {theme.get('theme_id')}")
    print(f"Theme Category: {theme.get('category')}")
    print(f"Theme Title: {theme.get('title')}")
    print(f"Hook Type: {theme.get('hook_type', 'SURPRISE')}")
    print(f"Structure: {theme.get('structure_type', 'HOOK → EXPLANATION → CTA')}")
    print(f"Angle: {theme.get('angle', '')}")
    print(f"Narration Master Text (Single Source of Truth): \"{narration_text}\"")

    # 1. TTS音声生成＆文単位タイムスタンプの取得（Nanami / Rate +0% / Pitch +0Hz 標準）
    tts_success, sentence_timeline = generate_voice_with_timeline(
        text=narration_text,
        output_path=NARRATION_PATH,
        voice_config={'voice': 'ja-JP-NanamiNeural', 'rate': '+0%', 'pitch': '+0Hz'}
    )

    if tts_success and sentence_timeline:
        print("[PIPELINE] TTS generation SUCCESS. Building synchronized dynamic scenes from narration.")
        dynamic_scenes = build_dynamic_scenes_from_timeline(sentence_timeline, total_video_duration=15.0)
        theme['scenes'] = dynamic_scenes

        # ナレーションと字幕の一致検証ログ出力
        reconstructed_text = "".join(sc['raw_text'] for sc in dynamic_scenes)
        is_exact_match = (narration_text == reconstructed_text)
        print(f"[VERIFICATION] Master Narration vs Subtitle Timeline Exact Match: {is_exact_match}")
        if not is_exact_match:
            print(f"[VERIFICATION WARNING] Narration: \"{narration_text}\"")
            print(f"[VERIFICATION WARNING] Subtitle:  \"{reconstructed_text}\"")

        # [VIDEO VARIATION] ログ出力
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
            print(f"  raw_text={sc['raw_text']}")
        print(f"Audio duration: {sentence_timeline[-1]['end']:.2f}s")
        print(f"Video duration: 15.00s\n")

    else:
        print("[PIPELINE] [FALLBACK ACTIVE] TTS generation FAILED. Using dynamic scenes from narration.")
        if os.path.exists(NARRATION_PATH):
            os.remove(NARRATION_PATH)
        dynamic_scenes = build_fallback_scenes_from_narration(narration_text, total_video_duration=15.0)
        theme['scenes'] = dynamic_scenes

    # 2. FFmpegによる合成
    build_shorts_video(
        input_video=input_video,
        output_video=output_video,
        theme=theme,
        narration_path=NARRATION_PATH if tts_success else None
    )

    # テーマ情報の更新保存
    try:
        with open(CURRENT_THEME_JSON, 'w', encoding='utf-8') as f:
            json.dump(theme, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[PIPELINE WARNING] Failed to save {CURRENT_THEME_JSON}: {e}")

    print("=== Pipeline Execution Complete ===")
    return output_video

def main():
    run_pipeline()

if __name__ == '__main__':
    main()
