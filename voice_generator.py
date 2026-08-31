import os
import sys
import re
import asyncio
import edge_tts
from pronunciation_dict import get_spoken_text

OUTPUT_DIR = "test_output"
DEFAULT_VOICE = "ja-JP-NanamiNeural"
DEFAULT_RATE = "+0%"
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
                "spoken_text": sentence_text,
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

def _split_into_display_sentences(text):
    """
    ナレーション原文を句読点（。！？）単位で分割し、句読点を保持した文リストを返す
    """
    raw_sentences = [s.strip() for s in re.split(r'([。！？!?])', text) if s.strip()]
    merged = []
    for s in raw_sentences:
        if s in ['。', '！', '？', '!', '?'] and merged:
            merged[-1] += s
        else:
            merged.append(s)
    return merged if merged else [text]

def generate_voice_with_timeline(text, output_path, voice_config=None, display_text=None):
    """
    ナレーション音声を生成し、文単位の正確な実音声タイムラインを返す。
    発音・プロソディ補正（pronunciation_dict）を適用し、画面字幕用の漢字表記（display_text）と
    TTS読み上げ用テキスト（spoken_text）を分離して処理する。
    """
    if voice_config is None:
        voice_config = {}

    if display_text is None:
        display_text = text

    voice = voice_config.get('voice', DEFAULT_VOICE)
    rate = voice_config.get('rate', DEFAULT_RATE)
    pitch = voice_config.get('pitch', DEFAULT_PITCH)

    # 発音補正＋プロソディ（ブレス）補正の適用（字幕原文は維持し、TTS用テキストのみ補正）
    spoken_text = get_spoken_text(text)

    print(f"[TTS] Generating narration with timeline from edge-tts...")
    print(f"[TTS] Voice: {voice}, Rate: {rate}, Pitch: {pitch}")
    print(f"[TTS] Display Text (字幕): \"{display_text}\"")
    print(f"[TTS] Spoken Text  (音声): \"{spoken_text}\"")

    try:
        sentences = asyncio.run(_generate_edge_tts_with_timeline(spoken_text, output_path, voice, rate, pitch))
        
        # 字幕表示用テキスト（原文の漢字表記）を各文のタイムラインにマッピング
        display_sentences = _split_into_display_sentences(display_text)
        for i, s in enumerate(sentences):
            if i < len(display_sentences):
                s['text'] = display_sentences[i]
                s['display_text'] = display_sentences[i]

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
    sample_text = "ふらつきやすい姿勢を整えたい方へ。自分の体重を利用したレッドコードで、体の奥の筋肉を刺激します。西田医院の取り組みはプロフィールから。"
    test_out = os.path.join(OUTPUT_DIR, "tts_prosody_test.mp3")
    ok, timeline = generate_voice_with_timeline(sample_text, test_out)
    for idx, sc in enumerate(timeline):
        print(f"Sentence {idx+1}: Display=\"{sc['text']}\" Spoken=\"{sc['spoken_text']}\" Time={sc['start']}s->{sc['end']}s")
