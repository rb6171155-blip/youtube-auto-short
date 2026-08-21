import os
import sys
import math
import struct
import wave
import json
import subprocess
import urllib.request
from PIL import Image, ImageDraw, ImageFont

INPUT_VIDEO = os.environ.get('INPUT_VIDEO', os.path.join('test_output', 'shorts_test.mp4'))
OUTPUT_VIDEO = os.environ.get('OUTPUT_VIDEO', os.path.join('test_output', 'tts_video_test.mp4'))
NARRATION_AUDIO = os.environ.get('NARRATION_AUDIO', os.path.join('test_output', 'narration.mp3'))
OUTPUT_DIR = 'test_output'
ASSETS_DIR = 'assets'

FONT_PATH_LOCAL = os.path.join(ASSETS_DIR, 'fonts', 'NotoSansJP-Bold.otf')

FONT_CANDIDATES = [
    FONT_PATH_LOCAL,
    os.path.join(ASSETS_DIR, 'fonts', 'NotoSansJP-Bold.ttf'),
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
    '/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc',
    '/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    '/usr/share/fonts/truetype/fonts-japanese-gothic.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    'C:/Windows/Fonts/meiryo.ttc',
    'C:/Windows/Fonts/msgothic.ttc'
]

# 代表テーマ「テーマ1-1：痛みの先にある生活」
DEFAULT_THEME = {
    'theme_id': 'theme_1_1_philosophy',
    'title': '痛みの先にある生活 #Shorts',
    'narration': '痛みを和らげること。それはゴールではなく、スタートです。西田医院では、あなたが笑顔で暮らし続けられるよう、生活の背景まで一緒に考えます。',
    'scenes': [
        {
            'start': 0.0,
            'end': 11.5,
            'tag': '西田医院が大切にしていること',
            'lines': ['痛みを減らし、', 'その先の生活へ。']
        },
        {
            'start': 11.5,
            'end': 15.0,
            'tag': '公式ホームページ・施設情報',
            'lines': ['詳しくは', 'プロフィールから']
        }
    ]
}

def ensure_font_available():
    for candidate in FONT_CANDIDATES:
        if os.path.exists(candidate):
            return candidate
    
    try:
        os.makedirs(os.path.dirname(FONT_PATH_LOCAL), exist_ok=True)
        print("Downloading NotoSansCJK font for Japanese rendering...")
        url = "https://raw.githubusercontent.com/googlefonts/noto-cjk/main/Sans/OTF/Japanese/NotoSansCJKjp-Bold.otf"
        urllib.request.urlretrieve(url, FONT_PATH_LOCAL)
        if os.path.exists(FONT_PATH_LOCAL):
            return FONT_PATH_LOCAL
    except Exception as e:
        print(f"Font download warning: {e}", file=sys.stderr)
    return None

def get_font(size):
    font_file = ensure_font_available()
    if font_file:
        try:
            return ImageFont.truetype(font_file, size)
        except Exception as e:
            print(f"Error loading font {font_file}: {e}", file=sys.stderr)
    
    for candidate in FONT_CANDIDATES:
        if os.path.exists(candidate):
            try:
                return ImageFont.truetype(candidate, size)
            except Exception:
                continue
    return ImageFont.load_default()

def create_scene_overlay(scene, index, output_dir):
    """
    1080x1920の透過キャンバス上に、半透明の角丸ボックスと字幕を描画（セーフエリア幅800px対応）
    """
    width, height = 1080, 1920
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    tag_font = get_font(28)
    main_font = get_font(54)

    # ボックス設定（画面中央〜下部付近・YouTube Shortsの右側UIと干渉しない幅800px）
    box_w = 800
    box_h = 340
    box_x = (width - box_w) // 2 # 左右マージン 140px（セーフエリア確保）
    box_y = 1180
    corner_radius = 28

    box_bg_color = (15, 28, 48, 200)       # rgba(15, 28, 48, 0.78)
    box_border_color = (255, 255, 255, 45) # 薄い境界線

    draw.rounded_rectangle(
        [box_x, box_y, box_x + box_w, box_y + box_h],
        radius=corner_radius,
        fill=box_bg_color,
        outline=box_border_color,
        width=2
    )

    tag_text = scene.get('tag', '')
    if tag_text and tag_font:
        bbox = draw.textbbox((0, 0), tag_text, font=tag_font)
        tag_w = bbox[2] - bbox[0]
        tag_h = bbox[3] - bbox[1]

        tag_badge_w = tag_w + 36
        tag_badge_h = tag_h + 16
        tag_badge_x = (width - tag_badge_w) // 2
        tag_badge_y = box_y + 32

        draw.rounded_rectangle(
            [tag_badge_x, tag_badge_y, tag_badge_x + tag_badge_w, tag_badge_y + tag_badge_h],
            radius=12,
            fill=(41, 98, 180, 220)
        )
        draw.text(
            (tag_badge_x + 18, tag_badge_y + 6),
            tag_text,
            font=tag_font,
            fill=(255, 255, 255, 255)
        )

    lines = scene.get('lines', [])
    if lines and main_font:
        line_spacing = 20
        line_heights = []
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=main_font)
            line_heights.append(bbox[3] - bbox[1])

        total_text_h = sum(line_heights) + line_spacing * (len(lines) - 1)
        text_start_y = box_y + 110 + (box_h - 110 - total_text_h) // 2

        current_y = text_start_y
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=main_font)
            line_w = bbox[2] - bbox[0]
            line_x = (width - line_w) // 2

            # ドロップシャドウ
            draw.text((line_x + 2, current_y + 2), line, font=main_font, fill=(0, 0, 0, 140))
            # 白文字メインテキスト
            draw.text((line_x, current_y), line, font=main_font, fill=(255, 255, 255, 255))

            current_y += line_heights[i] + line_spacing

    # 画面上部 固定ヘッダー
    header_font = get_font(32)
    if header_font:
        header_text = "医療法人 西田医院"
        h_bbox = draw.textbbox((0, 0), header_text, font=header_font)
        h_w = h_bbox[2] - h_bbox[0]
        h_h = h_bbox[3] - h_bbox[1]

        h_badge_w = h_w + 44
        h_badge_h = h_h + 20
        h_badge_x = (width - h_badge_w) // 2
        h_badge_y = 120

        draw.rounded_rectangle(
            [h_badge_x, h_badge_y, h_badge_x + h_badge_w, h_badge_y + h_badge_h],
            radius=16,
            fill=(15, 28, 48, 180),
            outline=(255, 255, 255, 40),
            width=1
        )
        draw.text((h_badge_x + 22, h_badge_y + 8), header_text, font=header_font, fill=(245, 248, 255, 255))

    overlay_file = os.path.join(output_dir, f"overlay_scene_{index}.png")
    img.save(overlay_file, "PNG")
    return overlay_file

def generate_gentle_bgm(output_path, duration=15.0, sample_rate=44100):
    if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
        return output_path

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    num_samples = int(duration * sample_rate)

    chord_progression = [
        [261.63, 329.63, 392.00, 523.25], # C4, E4, G4, C5
        [196.00, 246.94, 293.66, 392.00], # G3, B3, D4, G4
        [220.00, 261.63, 329.63, 440.00], # A3, C4, E4, A4
        [174.61, 220.00, 261.63, 349.23], # F3, A3, C4, F4
    ]
    chord_duration = duration / len(chord_progression)

    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        chord_idx = min(int(t / chord_duration), len(chord_progression) - 1)
        chord = chord_progression[chord_idx]
        local_t = t - (chord_idx * chord_duration)

        val = 0.0
        for note_idx, freq in enumerate(chord):
            note_t = max(0.0, local_t - note_idx * 0.18)
            if note_t > 0:
                envelope = math.exp(-note_t * 1.6)
                s1 = math.sin(2.0 * math.pi * freq * note_t)
                s2 = 0.35 * math.sin(2.0 * math.pi * freq * 2 * note_t)
                s3 = 0.12 * math.sin(2.0 * math.pi * freq * 3 * note_t)
                val += (s1 + s2 + s3) * envelope

        val = val * 0.14

        if t > (duration - 2.0):
            fade_ratio = max(0.0, (duration - t) / 2.0)
            val *= fade_ratio

        val = max(-1.0, min(1.0, val))
        samples.append(int(val * 32767.0))

    with wave.open(output_path, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        raw_data = struct.pack(f'<{len(samples)}h', *samples)
        wav_file.writeframes(raw_data)

    print(f"Generated gentle background audio: {output_path}")
    return output_path

def build_shorts_video(input_video, output_video, theme=DEFAULT_THEME, narration_path=NARRATION_AUDIO):
    if not os.path.exists(input_video):
        print(f"Error: Input video not found at {input_video}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(output_video), exist_ok=True)

    scenes = theme.get('scenes', [])

    overlay_files = []
    for idx, scene in enumerate(scenes):
        f = create_scene_overlay(scene, idx, OUTPUT_DIR)
        overlay_files.append(f)
        print(f"Created scene {idx + 1} overlay image: {f}")

    bgm_path = os.path.join(ASSETS_DIR, 'bgm', 'gentle_bgm.wav')
    generate_gentle_bgm(bgm_path, duration=15.0)

    has_narration = os.path.exists(narration_path) and os.path.getsize(narration_path) > 1000

    if has_narration:
        print(f"[AUDIO MODE] Narration mode active: {narration_path}")
        ffmpeg_inputs = ['ffmpeg', '-y', '-i', input_video, '-i', narration_path, '-i', bgm_path]
        overlay_start_idx = 3
    else:
        print("[AUDIO MODE] [FALLBACK] Narration audio not available. Falling back to subtitle + BGM mode.")
        ffmpeg_inputs = ['ffmpeg', '-y', '-i', input_video, '-i', bgm_path]
        overlay_start_idx = 2

    for ov in overlay_files:
        ffmpeg_inputs.extend(['-i', ov])

    filter_chains = []
    last_v = "[0:v]"
    for idx, scene in enumerate(scenes):
        in_idx = overlay_start_idx + idx
        next_v = f"[v{idx}]" if idx < len(scenes) - 1 else "[vout]"
        st = scene['start']
        et = scene['end']
        filter_chains.append(f"{last_v}[{in_idx}:v]overlay=enable='between(t,{st},{et})':format=auto{next_v}")
        last_v = next_v

    if has_narration:
        # ナレーション主音声(volume=1.0) + 控えめBGM(volume=0.06)
        filter_chains.append("[1:a]volume=1.0,afade=t=out:st=13:d=2[anarr]")
        filter_chains.append("[2:a]volume=0.06,afade=t=out:st=13:d=2[abgm]")
        filter_chains.append("[anarr][abgm]amix=inputs=2:duration=longest:dropout_transition=2[aout]")
    else:
        filter_chains.append("[1:a]volume=0.15,afade=t=out:st=13:d=2[aout]")

    filter_complex_str = "; ".join(filter_chains)

    cmd = ffmpeg_inputs + [
        '-filter_complex', filter_complex_str,
        '-map', '[vout]',
        '-map', '[aout]',
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '20',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-t', '15',
        output_video
    ]

    print("Executing ffmpeg composite render...")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"ffmpeg composite error:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    file_size = os.path.getsize(output_video)
    print(f"Composite render complete: {os.path.abspath(output_video)}")
    print(f"Rendered video size: {file_size} bytes")

    for idx, scene in enumerate(scenes):
        snap_time = (scene['start'] + scene['end']) / 2.0
        snap_path = os.path.join(OUTPUT_DIR, f"preview_scene_{idx + 1}.jpg")
        snap_cmd = [
            'ffmpeg', '-y',
            '-ss', str(snap_time),
            '-i', output_video,
            '-vframes', '1',
            '-q:v', '2',
            snap_path
        ]
        subprocess.run(snap_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if os.path.exists(snap_path):
            print(f"Extracted preview frame {idx + 1}: {snap_path}")

def main():
    build_shorts_video(INPUT_VIDEO, OUTPUT_VIDEO, DEFAULT_THEME, NARRATION_AUDIO)

if __name__ == '__main__':
    main()
