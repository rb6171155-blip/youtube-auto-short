import os
import sys
import asyncio
import edge_tts

OUTPUT_DIR = "test_output"
DEFAULT_VOICE = "ja-JP-NanamiNeural"
DEFAULT_RATE = "-5%"
DEFAULT_PITCH = "+0Hz"

async def _generate_edge_tts_with_timeline(text, output_path, voice=DEFAULT_VOICE, rate=DEFAULT_RATE, pitch=DEFAULT_PITCH):
    """
    edge-tts を非同期実行し、音声MP3を保存すると同時に
    SentenceBoundary メタデータから文単位の実音声タイムスタンプを取得する
    """
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    audio_data = bytearray()
    sentences = []

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data.extend(chunk["data"])
        elif chunk["type"] == "SentenceBoundary":
            # 100ナノ秒単位を秒（float）に変換
            start_sec = chunk["offset"] / 10_000_000.0
            dur_sec = chunk["duration"] / 10_000_000.0
            end_sec = start_sec + dur_sec
            sentence_text = chunk["text"]
            sentences.append({
                "text": sentence_text,
                "start": round(start_sec, 2),
                "end": round(end_sec, 2),
                "duration": round(dur_sec, 2)
            })

    if not audio_data:
        raise ValueError("No audio data received from edge-tts")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(audio_data)

    return sentences

def generate_voice_with_timeline(text, output_path, voice_config=None):
    """
    ナレーション音声を生成し、文単位の正確な実音声タイムラインを返す
    """
    if voice_config is None:
        voice_config = {}

    voice = voice_config.get('voice', DEFAULT_VOICE)
    rate = voice_config.get('rate', DEFAULT_RATE)
    pitch = voice_config.get('pitch', DEFAULT_PITCH)

    print(f"[TTS] Generating narration with timeline from edge-tts...")
    print(f"[TTS] Voice: {voice}, Rate: {rate}, Pitch: {pitch}")
    print(f"[TTS] Text: \"{text}\"")

    try:
        sentences = asyncio.run(_generate_edge_tts_with_timeline(text, output_path, voice, rate, pitch))
        file_size = os.path.getsize(output_path)
        print(f"[TTS SUCCESS] Generated: {output_path} ({file_size} bytes, {len(sentences)} sentences)")
        return True, sentences
    except Exception as e:
        print(f"[TTS ERROR] Failed to generate TTS with timeline: {e}", file=sys.stderr)
        return False, []

def generate_voice(text, output_path, provider="edge", voice_config=None):
    """
    既存の互換性用ラッパー関数
    """
    success, _ = generate_voice_with_timeline(text, output_path, voice_config)
    return success

if __name__ == '__main__':
    sample_text = "痛みを和らげること。それはゴールではなく、スタートです。西田医院では、あなたが笑顔で暮らせるよう一緒に考えます。詳しくはプロフィールへ。"
    test_out = os.path.join(OUTPUT_DIR, "tts_timeline_test.mp3")
    ok, timeline = generate_voice_with_timeline(sample_text, test_out)
    print("Timeline result:", json.dumps(timeline, ensure_ascii=False, indent=2))
