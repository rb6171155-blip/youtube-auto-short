import os
import sys
import asyncio
import time

DEFAULT_VOICE_CONFIG = {
    'provider': 'edge',
    'voice': 'ja-JP-NanamiNeural',
    'rate': '-5%', # 落ち着きと温かみのある話速
    'pitch': '+0Hz'
}

async def _generate_edge_tts(text, voice, rate, pitch, output_path):
    import edge_tts
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await communicate.save(output_path)

def generate_voice(text, output_path, provider="edge", voice_config=None):
    """
    TTS音声を生成する汎用インターフェース。
    将来的にGoogle Cloud TTSやAzure AI Speech等へ差し替え可能な疎結合設計。
    失敗時は例外でクラッシュせず、Falseを返してフォールバックを促す。
    """
    if not text:
        print("[TTS WARNING] Text is empty. Skipping voice generation.", file=sys.stderr)
        return False

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    cfg = DEFAULT_VOICE_CONFIG.copy()
    if voice_config:
        cfg.update(voice_config)

    print(f"[TTS] Generating narration with provider '{provider}'...")
    print(f"[TTS] Voice: {cfg['voice']}, Rate: {cfg['rate']}, Pitch: {cfg['pitch']}")
    print(f"[TTS] Text: \"{text}\"")

    t0 = time.time()
    try:
        if provider == "edge":
            asyncio.run(_generate_edge_tts(
                text=text,
                voice=cfg['voice'],
                rate=cfg['rate'],
                pitch=cfg['pitch'],
                output_path=output_path
            ))
        else:
            print(f"[TTS WARNING] Unknown provider '{provider}'. Falling back.", file=sys.stderr)
            return False

        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            elapsed = time.time() - t0
            file_size = os.path.getsize(output_path)
            print(f"[TTS SUCCESS] Generated: {output_path} ({file_size} bytes in {elapsed:.2f}s)")
            return True
        else:
            print(f"[TTS WARNING] Generated audio file is empty or invalid: {output_path}", file=sys.stderr)
            return False

    except Exception as e:
        elapsed = time.time() - t0
        print(f"[TTS WARNING] edge-tts generation failed after {elapsed:.2f}s: {e}", file=sys.stderr)
        print("[TTS WARNING] Falling back to subtitle + BGM mode.", file=sys.stderr)
        return False

if __name__ == '__main__':
    test_text = "西田医院が大切にしているのは、治療だけではありません。その先の生活まで、一緒に支えることです。"
    test_out = os.path.join("test_output", "narration.mp3")
    res = generate_voice(test_text, test_out)
    print(f"Result: {res}")
