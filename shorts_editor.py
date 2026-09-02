import os
import sys
import math
import struct
import wave
import subprocess
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = "test_output"
ASSETS_DIR = "assets"

def get_font(size):
    """
    極太で視認性の高い日本語フォントを優先探索してロードする。
    Ubuntu/GitHub Actions（NotoSansCJK-Bold）および Windows（Meiryo Bold / Yu Gothic Bold）の両環境に対応。
    """
    candidates = [
        # Ubuntu / Linux (GitHub Actions)
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
        # Windows
        "C:\\Windows\\Fonts\\meiryob.ttc",
        "C:\\Windows\\Fonts\\yugothb.ttc",
        "C:\\Windows\\Fonts\\meiryo.ttc",
        "C:\\Windows\\Fonts\\msgothic.ttc",
        "C:\\Windows\\Fonts\\yu-gothic-bold.ttf",
        "C:\\Windows\\Fonts\\arial.ttf"
    ]
    for font_path in candidates:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                continue
    return ImageFont.load_default()

def create_scene_overlay(scene, index, output_dir):
    """
    1080x1920の透過キャンバス上に、ナレーション同期字幕を描画（セーフエリア幅840px対応）
    ※字幕位置を画面上部（YouTube Shortsの下部・右側UIを避けた上方セーフエリア）へ配置、枠なし
    """
    width, height = 1080, 1920
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # メイン字幕フォント（視認性の高い極太 54pt）
    main_font = get_font(54)

    # 字幕配置エリア設定（画面上方セーフエリア：ブランドヘッダー下付近）
    box_w = 860
    box_h = 280
    box_x = (width - box_w) // 2 # 左右マージン 110px
    box_y = 260                  # 画面上方

    # メイン字幕テキスト描画（画面上部・高視認性ドロップシャドウ付き白文字）
    lines = scene.get('lines', [])
    if lines and main_font:
        line_spacing = 22
        line_heights = []
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=main_font)
            line_heights.append(bbox[3] - bbox[1])

        total_text_h = sum(line_heights) + line_spacing * (len(lines) - 1)
        text_start_y = box_y + (box_h - total_text_h) // 2

        current_y = text_start_y
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=main_font)
            line_w = bbox[2] - bbox[0]
            line_x = (width - line_w) // 2

            # 高視認性ドロップシャドウ（全周囲多重アウトラインシャドウで背景動画から完全に浮き立たせる）
            shadow_offsets = [
                (-3, 0), (3, 0), (0, -3), (0, 3),
                (-3, -3), (3, 3), (-3, 3), (3, -3),
                (-2, -2), (2, 2), (-2, 2), (2, -2),
                (0, 4), (0, 5), (3, 4), (-3, 4)
            ]
            for dx, dy in shadow_offsets:
                draw.text((line_x + dx, current_y + dy), line, font=main_font, fill=(0, 0, 0, 230))

            # 白文字メインテキスト
            draw.text((line_x, current_y), line, font=main_font, fill=(255, 255, 255, 255))

            current_y += line_heights[i] + line_spacing

    # 画面上部 固定ヘッダー（「医療法人 西田医院」公式ブランド表示）
    # ※フォントサイズを約2倍（30pt -> 56pt）に拡大
    header_font = get_font(56)
    if header_font:
        header_text = "医療法人 西田医院"
        h_bbox = draw.textbbox((0, 0), header_text, font=header_font)
        h_w = h_bbox[2] - h_bbox[0]
        h_h = h_bbox[3] - h_bbox[1]

        h_badge_w = h_w + 56
        h_badge_h = h_h + 26
        h_badge_x = (width - h_badge_w) // 2
        h_badge_y = 100

        draw.rounded_rectangle(
            [h_badge_x, h_badge_y, h_badge_x + h_badge_w, h_badge_y + h_badge_h],
            radius=18,
            fill=(12, 24, 42, 205),
            outline=(255, 255, 255, 55),
            width=2
        )
        draw.text((h_badge_x + 28, h_badge_y + 11), header_text, font=header_font, fill=(245, 248, 255, 255))

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

def build_shorts_video(input_video, output_video, theme=None, narration_path=None):
    if not os.path.exists(input_video):
        print(f"Error: Input video not found at {input_video}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(output_video), exist_ok=True)

    if theme is None:
        from themes import DEFAULT_THEME
        theme = DEFAULT_THEME

    scenes = theme.get('scenes', [])

    # レンダリング直前でのタイムコード・クランプ処理（直前の終了 <= 次の開始を二重保証）
    num_scenes = len(scenes)
    for idx in range(num_scenes - 1):
        scenes[idx]['end'] = min(scenes[idx]['end'], scenes[idx + 1]['start'])

    overlay_files = []
    for idx, scene in enumerate(scenes):
        f = create_scene_overlay(scene, idx, OUTPUT_DIR)
        overlay_files.append(f)
        print(f"Created scene {idx + 1} overlay image: {f}")

    bgm_path = os.path.join(ASSETS_DIR, 'bgm', 'gentle_bgm.wav')
    generate_gentle_bgm(bgm_path, duration=15.0)

    has_narration = narration_path and os.path.exists(narration_path) and os.path.getsize(narration_path) > 1000

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

    # レンダリング時のオーバーラップ完全防止フィルター
    # 途中シーン: gte(t, st) * lt(t, et) （半開区間 [st, et) とすることで境界フレームでの重複描画を0に抑制）
    # 最終シーン: gte(t, st) * lte(t, et) （動画末尾まで完全表示）
    filter_chains = []
    last_v = "[0:v]"
    for idx, scene in enumerate(scenes):
        in_idx = overlay_start_idx + idx
        next_v = f"[v{idx}]" if idx < num_scenes - 1 else "[vout]"
        st = scene['start']
        et = scene['end']
        if idx < num_scenes - 1:
            enable_expr = f"gte(t\\,{st})*lt(t\\,{et})"
        else:
            enable_expr = f"gte(t\\,{st})*lte(t\\,{et})"
        filter_chains.append(f"{last_v}[{in_idx}:v]overlay=enable='{enable_expr}':format=auto{next_v}")
        last_v = next_v

    if has_narration:
        filter_chains.append("[1:a]volume=1.0,afade=t=out:st=13.5:d=1.5[anarr]")
        filter_chains.append("[2:a]volume=0.06,afade=t=out:st=13.5:d=1.5[abgm]")
        filter_chains.append("[anarr][abgm]amix=inputs=2:duration=longest:dropout_transition=2[aout]")
    else:
        filter_chains.append("[1:a]volume=0.15,afade=t=out:st=13.5:d=1.5[aout]")

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
    pass

if __name__ == '__main__':
    main()
