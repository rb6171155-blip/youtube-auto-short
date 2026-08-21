import os
import sys
import subprocess
import json

INPUT_PATH = os.path.join('test_output', 'pexels_test.mp4')
OUTPUT_PATH = os.path.join('test_output', 'shorts_test.mp4')

def get_video_dimensions(file_path):
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height',
        '-of', 'json',
        file_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    data = json.loads(result.stdout)
    width = data['streams'][0]['width']
    height = data['streams'][0]['height']
    return int(width), int(height)

def convert_to_9_16(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"Error: Input video not found at {input_path}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    in_w, in_h = get_video_dimensions(input_path)
    print(f"Input video dimensions: {in_w}x{in_h} (Aspect ratio: {in_w/in_h:.4f})")

    vf_filter = "crop=min(iw\\,ih*9/16):min(ih\\,iw*16/9),scale=1080:1920"

    cmd = [
        'ffmpeg',
        '-y',
        '-i', input_path,
        '-vf', vf_filter,
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '22',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac',
        output_path
    ]

    print("Converting video to 9:16 format with ffmpeg...")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"ffmpeg error:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    out_w, out_h = get_video_dimensions(output_path)
    aspect_ratio = out_w / out_h
    file_size = os.path.getsize(output_path)
    print(f"Output video dimensions: {out_w}x{out_h} (Aspect ratio: {aspect_ratio:.4f})")
    print(f"Output file size: {file_size} bytes")

    if out_w == 1080 and out_h == 1920:
        print("Verification: Output video is exactly 1080x1920 (9:16). Conversion successful.")
    else:
        print(f"Verification: Aspect ratio is {aspect_ratio:.4f}.")

def main():
    convert_to_9_16(INPUT_PATH, OUTPUT_PATH)

if __name__ == '__main__':
    main()
