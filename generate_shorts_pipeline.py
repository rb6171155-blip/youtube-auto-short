import os
import sys
from voice_generator import generate_voice
from shorts_editor import build_shorts_video, DEFAULT_THEME

INPUT_VIDEO = os.environ.get('INPUT_VIDEO', os.path.join('test_output', 'shorts_test.mp4'))
OUTPUT_VIDEO = os.environ.get('OUTPUT_VIDEO', os.path.join('test_output', 'tts_video_test.mp4'))
NARRATION_PATH = os.path.join('test_output', 'narration.mp3')

def run_pipeline(theme=DEFAULT_THEME, input_video=INPUT_VIDEO, output_video=OUTPUT_VIDEO):
    print("=== YouTube Shorts Generation Pipeline ===")
    print(f"Theme Title: {theme.get('title')}")
    print(f"Narration Text: {theme.get('narration')}")

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

if __name__ == '__main__':
    run_pipeline()
