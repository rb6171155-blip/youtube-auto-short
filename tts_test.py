import os
import sys
import asyncio
import time
import edge_tts

OUTPUT_DIR = os.path.join('test_output', 'tts_samples')

TEST_TEXTS = {
    'standard': "西田医院が大切にしているのは、治療だけではありません。その先の生活まで、一緒に支えることです。",
    'pause_adjusted': "西田医院が大切にしているのは、治療だけではありません。……その先の生活まで、一緒に支えることです。",
    'spoken_friendly': "西田医院が大切にしているのは、治療だけではありません。その先の生活まで、しっかりと支えることです。"
}

VOICE_CONFIGS = [
    {
        'id': 'nanami_standard_default',
        'voice': 'ja-JP-NanamiNeural',
        'rate': '+0%',
        'pitch': '+0Hz',
        'text_key': 'standard',
        'desc': 'Nanami (女性・標準原稿・速度通常)'
    },
    {
        'id': 'nanami_standard_slow',
        'voice': 'ja-JP-NanamiNeural',
        'rate': '-5%',
        'pitch': '+0Hz',
        'text_key': 'standard',
        'desc': 'Nanami (女性・標準原稿・速度-5%落ち着き)'
    },
    {
        'id': 'nanami_standard_fast',
        'voice': 'ja-JP-NanamiNeural',
        'rate': '+10%',
        'pitch': '+0Hz',
        'text_key': 'standard',
        'desc': 'Nanami (女性・標準原稿・速度+10%Shorts向け)'
    },
    {
        'id': 'nanami_pause_adjusted',
        'voice': 'ja-JP-NanamiNeural',
        'rate': '+0%',
        'pitch': '+0Hz',
        'text_key': 'pause_adjusted',
        'desc': 'Nanami (女性・間調整原稿・速度通常)'
    },
    {
        'id': 'keita_standard_default',
        'voice': 'ja-JP-KeitaNeural',
        'rate': '+0%',
        'pitch': '+0Hz',
        'text_key': 'standard',
        'desc': 'Keita (男性・標準原稿・速度通常)'
    },
    {
        'id': 'keita_standard_slow',
        'voice': 'ja-JP-KeitaNeural',
        'rate': '-5%',
        'pitch': '+0Hz',
        'text_key': 'standard',
        'desc': 'Keita (男性・標準原稿・速度-5%信頼感)'
    }
]

async def generate_voice_edge(text, voice, rate, pitch, output_path):
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await communicate.save(output_path)

def get_audio_duration_rough(file_path):
    size_bytes = os.path.getsize(file_path)
    # 48kbps MP3 (約6000バイト/秒)
    duration_est = size_bytes / 6000.0
    return duration_est

async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("=== Japanese AI Voice Narration TTS Quality Test ===")
    print(f"Output directory: {os.path.abspath(OUTPUT_DIR)}\n")

    results = []

    for cfg in VOICE_CONFIGS:
        text = TEST_TEXTS[cfg['text_key']]
        file_name = f"{cfg['id']}.mp3"
        out_path = os.path.join(OUTPUT_DIR, file_name)

        print(f"Generating: {cfg['desc']} ...")
        t0 = time.time()
        try:
            await generate_voice_edge(text, cfg['voice'], cfg['rate'], cfg['pitch'], out_path)
            elapsed = time.time() - t0
            file_size = os.path.getsize(out_path)
            duration_est = get_audio_duration_rough(out_path)

            print(f" -> Success! Elapsed: {elapsed:.2f}s, Size: {file_size} bytes (est: ~{duration_est:.1f}s)")
            results.append({
                'id': cfg['id'],
                'desc': cfg['desc'],
                'voice': cfg['voice'],
                'rate': cfg['rate'],
                'file': file_name,
                'size': file_size,
                'duration': f"{duration_est:.1f}s",
                'elapsed': f"{elapsed:.2f}s",
                'status': 'SUCCESS'
            })
        except Exception as e:
            elapsed = time.time() - t0
            print(f" -> Failed! Error: {e}", file=sys.stderr)
            results.append({
                'id': cfg['id'],
                'desc': cfg['desc'],
                'status': f'FAILED: {e}'
            })

    print("\n=== Generation Summary ===")
    for r in results:
        print(f"[{r['status']}] {r['desc']} -> {r.get('file', '')} (Time: {r.get('elapsed', 0)}, Duration: {r.get('duration', '')})")

if __name__ == '__main__':
    asyncio.run(main())
