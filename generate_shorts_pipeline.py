import os
import sys
import json
from voice_generator import generate_voice
from shorts_editor import build_shorts_video
from themes import DEFAULT_THEME, get_theme_by_id, get_all_themes, select_next_theme

INPUT_VIDEO = os.environ.get('INPUT_VIDEO', os.path.join('test_output', 'shorts_test.mp4'))
OUTPUT_VIDEO = os.environ.get('OUTPUT_VIDEO', os.path.join('test_output', 'tts_video_test.mp4'))
NARRATION_PATH = os.path.join('test_output', 'narration.mp3')
CURRENT_THEME_JSON = os.path.join('test_output', 'current_theme.json')

def run_pipeline(theme=None, input_video=INPUT_VIDEO, output_video=OUTPUT_VIDEO):
    # テーマが指定されていない場合は、未確定の状態で次回テーマを選択（投稿成功後に確定）
    if theme is None:
        theme = select_next_theme()

    print("=== YouTube Shorts Generation Pipeline ===")
    print(f"Theme ID: {theme.get('theme_id')}")
    print(f"Theme Category: {theme.get('category')}")
    print(f"Theme Title: {theme.get('title')}")
    print(f"Narration Text: {theme.get('narration')}")

    # 後続ステップ（YouTube アップロード等）のために現在テーマ情報を一時保存
    os.makedirs(os.path.dirname(os.path.abspath(CURRENT_THEME_JSON)), exist_ok=True)
    with open(CURRENT_THEME_JSON, 'w', encoding='utf-8') as f:
        json.dump(theme, f, ensure_ascii=False, indent=2)

    # 1. TTS音声生成（疎結合・フォールバック対応）
    narration_text = theme.get('narration', '')
    tts_success = generate_voice(
        text=narration_text,
        output_path=NARRATION_PATH,
        provider="edge",
        voice_config={'voice': 'ja-JP-NanamiNeural', 'rate': '-5%'}
    )

    if tts_success:
        print("[PIPELINE] TTS generation SUCCESS. Building video with narration + BGM.")
    else:
        print("[PIPELINE] [FALLBACK ACTIVE] TTS generation FAILED. Building video in subtitle + BGM mode.")
        if os.path.exists(NARRATION_PATH):
            os.remove(NARRATION_PATH)

    # 2. 動画合成レンダリング
    build_shorts_video(
        input_video=input_video,
        output_video=output_video,
        theme=theme,
        narration_path=NARRATION_PATH
    )

    print("=== Pipeline Execution Complete ===")
    return theme

if __name__ == '__main__':
    run_pipeline()
