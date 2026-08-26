import os
import sys
import requests
from themes import get_theme_by_id, select_next_theme

PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY')
OUTPUT_DIR = 'test_output'

def get_target_query():
    """
    現在選択されているテーマから bg_query を動的に取得する。
    THEME_ID 環境変数が指定されていればそのテーマを、
    指定がなければ本番用の select_next_theme() から取得する。
    テーマまたは bg_query が取得できない場合は安全のためエラーとして停止する。
    """
    env_theme_id = os.environ.get('THEME_ID', '').strip()
    if env_theme_id:
        theme = get_theme_by_id(env_theme_id)
        print(f"[PEXELS DOWNLOAD] Using specified THEME_ID: {env_theme_id}")
    else:
        theme = select_next_theme()
        print(f"[PEXELS DOWNLOAD] Using current rotation theme: {theme.get('theme_id')}")

    if not theme:
        print("[PEXELS ERROR] Failed to determine theme. Aborting download to prevent irrelevant video selection.", file=sys.stderr)
        sys.exit(1)

    bg_query = theme.get('bg_query', '').strip()
    if not bg_query:
        print(f"[PEXELS ERROR] Theme '{theme.get('theme_id')}' has no bg_query defined. Aborting.", file=sys.stderr)
        sys.exit(1)

    print(f"[PEXELS DOWNLOAD] Target theme: '{theme.get('theme_id')}' ({theme.get('title')})")
    print(f"[PEXELS DOWNLOAD] Dynamically resolved search query: '{bg_query}'")
    return bg_query, theme

def main():
    if not PEXELS_API_KEY:
        print("Error: PEXELS_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    search_query, theme = get_target_query()

    # 縦向き動画を優先して複数件（per_page=15）検索
    url = f"https://api.pexels.com/videos/search?query={requests.utils.quote(search_query)}&per_page=15&orientation=portrait"
    headers = {
        "Authorization": PEXELS_API_KEY
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()

        videos = data.get('videos', [])
        # 縦向きで見つからない場合は標準検索（orientationなし）を試行
        if not videos:
            print(f"[PEXELS INFO] No portrait videos found for '{search_query}'. Trying general search...")
            fallback_url = f"https://api.pexels.com/videos/search?query={requests.utils.quote(search_query)}&per_page=15"
            fb_res = requests.get(fallback_url, headers=headers, timeout=15)
            fb_res.raise_for_status()
            videos = fb_res.json().get('videos', [])

        if not videos:
            print(f"[PEXELS ERROR] No videos found for query: '{search_query}'. Aborting generation.", file=sys.stderr)
            sys.exit(1)

        # 最低10秒以上の動画を優先選定
        selected_video = None
        for v in videos:
            if v.get('duration', 0) >= 10:
                selected_video = v
                break
        if not selected_video:
            selected_video = videos[0]

        video_files = selected_video.get('video_files', [])
        if not video_files:
            print("[PEXELS ERROR] No video files found in the selected result.", file=sys.stderr)
            sys.exit(1)

        # HDまたは適切なmp4ファイルを選択（幅または高さが大きい高画質を優先）
        chosen_file = None
        # 1. 縦型Shorts解像度（720x1280以上）のmp4を優先
        for vf in video_files:
            if vf.get('file_type') == 'video/mp4' and vf.get('height', 0) >= 1280:
                chosen_file = vf
                break
        # 2. HD品質のmp4
        if not chosen_file:
            for vf in video_files:
                if vf.get('quality') == 'hd' and vf.get('file_type') == 'video/mp4':
                    chosen_file = vf
                    break
        # 3. 任意のmp4
        if not chosen_file:
            for vf in video_files:
                if vf.get('file_type') == 'video/mp4':
                    chosen_file = vf
                    break
        if not chosen_file:
            chosen_file = video_files[0]

        download_url = chosen_file.get('link')
        if not download_url:
            print("[PEXELS ERROR] No download link available for the video.", file=sys.stderr)
            sys.exit(1)

        output_file_path = os.path.join(OUTPUT_DIR, 'pexels_test.mp4')
        print(f"[PEXELS SUCCESS] Selected Video ID: {selected_video.get('id')}, Duration: {selected_video.get('duration')}s, Res: {chosen_file.get('width')}x{chosen_file.get('height')}")
        print("Downloading video from Pexels API...")

        video_response = requests.get(download_url, stream=True, timeout=30)
        video_response.raise_for_status()

        with open(output_file_path, 'wb') as f:
            for chunk in video_response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        file_size = os.path.getsize(output_file_path)
        print(f"Download complete: {os.path.abspath(output_file_path)}")
        print(f"Video file size: {file_size:,} bytes")

    except Exception as e:
        print(f"[PEXELS ERROR] An error occurred during download: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
