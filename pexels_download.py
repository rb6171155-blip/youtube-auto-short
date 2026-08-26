import os
import sys
import json
import requests
from themes import get_theme_by_id, select_next_theme

PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY')
OUTPUT_DIR = 'test_output'
CURRENT_THEME_JSON = os.path.join(OUTPUT_DIR, 'current_theme.json')

def get_target_theme_and_queries():
    """
    現在選択されているテーマから、字幕・ナレーション内容に直接合致する優先検索クエリリストを取得する。
    選定されたテーマ情報は test_output/current_theme.json に保存し、
    後続の generate_shorts_pipeline.py と 100% 同一のバリエーションを共有する。
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

    # 優先度順の検索クエリリスト（bg_queries または bg_query）
    queries = theme.get('bg_queries', [])
    primary_query = theme.get('bg_query', '').strip()
    
    if primary_query and primary_query not in queries:
        queries = [primary_query] + queries
    elif not queries and primary_query:
        queries = [primary_query]

    if not queries:
        print(f"[PEXELS ERROR] Theme '{theme.get('theme_id')}' has no search queries defined. Aborting.", file=sys.stderr)
        sys.exit(1)

    # 選定テーマ情報を保存してパイプライン全体で同期
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    try:
        with open(CURRENT_THEME_JSON, 'w', encoding='utf-8') as f:
            json.dump(theme, f, ensure_ascii=False, indent=2)
        print(f"[PEXELS SYNC] Saved selected theme to {CURRENT_THEME_JSON}")
    except Exception as e:
        print(f"[PEXELS WARNING] Could not save current_theme.json: {e}")

    print(f"[PEXELS DOWNLOAD] Target theme: '{theme.get('theme_id')}' ({theme.get('title')})")
    print(f"[PEXELS DOWNLOAD] Priority search queries: {queries}")
    return queries, theme

def search_and_download_video(queries, output_file_path):
    headers = {
        "Authorization": PEXELS_API_KEY
    }

    chosen_file = None
    selected_video = None
    matched_query = None

    for q in queries:
        q_clean = q.strip()
        if not q_clean:
            continue

        print(f"[PEXELS SEARCH] Trying priority query: '{q_clean}' (orientation=portrait)...")
        url = f"https://api.pexels.com/videos/search?query={requests.utils.quote(q_clean)}&per_page=15&orientation=portrait"
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            videos = data.get('videos', [])

            # 縦向きで見つからない場合は標準検索も試行
            if not videos:
                print(f"[PEXELS SEARCH] No portrait videos for '{q_clean}'. Trying general search...")
                fallback_url = f"https://api.pexels.com/videos/search?query={requests.utils.quote(q_clean)}&per_page=15"
                fb_res = requests.get(fallback_url, headers=headers, timeout=15)
                fb_res.raise_for_status()
                videos = fb_res.json().get('videos', [])

            if not videos:
                print(f"[PEXELS SEARCH] 0 results for '{q_clean}'. Moving to next candidate query...")
                continue

            # 最低10秒以上の動画を優先選定
            candidates = [v for v in videos if v.get('duration', 0) >= 10]
            if not candidates:
                candidates = videos

            for v in candidates:
                video_files = v.get('video_files', [])
                # 1. 縦型解像度（高さ1280以上）のmp4
                for vf in video_files:
                    if vf.get('file_type') == 'video/mp4' and vf.get('height', 0) >= 1280:
                        chosen_file = vf
                        selected_video = v
                        matched_query = q_clean
                        break
                if chosen_file:
                    break
                # 2. HD mp4
                for vf in video_files:
                    if vf.get('quality') == 'hd' and vf.get('file_type') == 'video/mp4':
                        chosen_file = vf
                        selected_video = v
                        matched_query = q_clean
                        break
                if chosen_file:
                    break
                # 3. 任意のmp4
                for vf in video_files:
                    if vf.get('file_type') == 'video/mp4':
                        chosen_file = vf
                        selected_video = v
                        matched_query = q_clean
                        break
                if chosen_file:
                    break

            if chosen_file and selected_video:
                print(f"[PEXELS MATCH SUCCESS] Found suitable video with query '{matched_query}'!")
                break

        except Exception as e:
            print(f"[PEXELS WARNING] Search error for query '{q_clean}': {e}. Trying next...")
            continue

    if not chosen_file or not selected_video:
        print(f"[PEXELS ERROR] Failed to find any suitable video across queries: {queries}. Aborting.", file=sys.stderr)
        sys.exit(1)

    download_url = chosen_file.get('link')
    if not download_url:
        print("[PEXELS ERROR] No download link available for the video.", file=sys.stderr)
        sys.exit(1)

    print(f"[PEXELS SUCCESS] Selected Video ID: {selected_video.get('id')}, Duration: {selected_video.get('duration')}s, Resolution: {chosen_file.get('width')}x{chosen_file.get('height')}")
    print(f"[PEXELS SUCCESS] Video URL: {selected_video.get('url')}")
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

def main():
    if not PEXELS_API_KEY:
        print("Error: PEXELS_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    queries, theme = get_target_theme_and_queries()
    output_file_path = os.path.join(OUTPUT_DIR, 'pexels_test.mp4')
    search_and_download_video(queries, output_file_path)

if __name__ == '__main__':
    main()
