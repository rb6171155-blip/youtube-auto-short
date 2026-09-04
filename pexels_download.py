"""
Pexels自然・癒し系背景動画取得モジュール (Nature Background Video Downloader)

【設計方針】
1. 台本（ナレーション・字幕・テーマ順序・タイトル）は一切変更せず100%維持する。
2. 背景動画は、医療・リハビリ・人物・人工物・トレーニング映像を完全に排除し、
   「若葉・新緑・森・木漏れ日・青空・草原・花・水面・山」等の高品質な自然・癒し系映像のみを自動取得する。
3. 自然系キーワードプールから動的に検索し、除外フィルター（人物/医療/ジム/建物/CG等）を通過した候補からランダム選定する。
4. 過去に使用した動画IDを state/used_video_ids.json に記録し、重複使用を防止する。
5. 自然系以外の動画への妥協フォールバックは禁止し、多段階の自然系クエリ探索を行う。
"""

import os
import sys
import json
import random
import re
import requests
from themes import get_theme_by_id, select_next_theme

PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY')
OUTPUT_DIR = 'test_output'
CURRENT_THEME_JSON = os.path.join(OUTPUT_DIR, 'current_theme.json')
STATE_DIR = 'state'
USED_VIDEOS_JSON = os.path.join(STATE_DIR, 'used_video_ids.json')
MAX_USED_HISTORY = 60

# ==============================================================================
# 自然・癒し系検索キーワードプール（厳選された高品質な自然映像クエリ）
# ==============================================================================
NATURE_QUERY_POOLS = [
    # 若葉・新緑・木漏れ日・森
    "fresh green leaves sunlight",
    "sunlight through forest trees",
    "peaceful green forest canopy",
    "green leaves moving in wind",
    "young green leaves sunny day",
    "green tree branches breeze nature",
    "serene forest walk sunlight",
    
    # 青空・白い雲・空
    "blue sky white clouds timelapse",
    "clear blue sky summer sunny day",
    "peaceful sky sun rays nature",
    "fluffy white clouds blue sky",
    
    # 草原・花・自然の風
    "green meadow grass in breeze",
    "blooming wild flowers sunny field",
    "peaceful green field nature landscape",
    "flowers meadow gentle wind",
    
    # 水面・湖・川・穏やかな波
    "calm lake water reflection nature",
    "peaceful river water flowing forest",
    "gentle ocean waves sunny beach",
    "calm sea water ripple sunlight",
    "crystal clear mountain stream nature",
    
    # 山・朝の光・穏やかな風景
    "peaceful mountain landscape sunrise",
    "morning sunlight nature landscape",
    "green hills landscape blue sky sunny",
    "relaxing nature scenic view serene"
]

# ==============================================================================
# 不適切映像の除外キーワード（人物・医療・ジム・人工物・CG等）
# ==============================================================================
EXCLUSION_WORDS = [
    # 人物・顔・医療
    "doctor", "patient", "nurse", "hospital", "clinic", "medical", "surgery",
    "face", "portrait", "woman", "women", "man", "men", "girl", "boy", "person", "people",
    "model", "talking", "elderly", "senior", "human", "body", "hands", "feet", "head",
    
    # フィットネス・トレーニング・スポーツ
    "gym", "fitness", "workout", "bodybuilding", "exercise", "training",
    "muscle", "athlete", "weight", "running", "jogging", "sports", "yoga", "crossfit",
    "stretching", "pushup", "squat",
    
    # 人工物・都市・乗り物・機械
    "building", "city", "street", "car", "traffic", "office", "computer",
    "phone", "laptop", "room", "indoor", "house", "road", "train", "machine", "factory",
    "desk", "screen", "technology", "urban",
    
    # CG・アニメーション・不適切映像
    "animation", "3d", "cg", "render", "abstract", "neon", "commercial",
    "dark", "nightclub", "horror", "blood", "fire", "smoke", "creepy"
]

def load_used_video_ids():
    """過去に使用した動画IDリストをロードする"""
    if os.path.exists(USED_VIDEOS_JSON):
        try:
            with open(USED_VIDEOS_JSON, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('used_ids', []))
        except Exception as e:
            print(f"[PEXELS WARNING] Failed to read {USED_VIDEOS_JSON}: {e}")
    return set()

def save_used_video_id(video_id):
    """採用された動画IDを記録し保存する"""
    os.makedirs(STATE_DIR, exist_ok=True)
    used_ids = list(load_used_video_ids())
    if video_id in used_ids:
        used_ids.remove(video_id)
    used_ids.append(video_id)
    
    # 履歴上限の保持
    if len(used_ids) > MAX_USED_HISTORY:
        used_ids = used_ids[-MAX_USED_HISTORY:]
        
    try:
        with open(USED_VIDEOS_JSON, 'w', encoding='utf-8') as f:
            json.dump({'used_ids': used_ids, 'max_history': MAX_USED_HISTORY}, f, ensure_ascii=False, indent=2)
        print(f"[PEXELS STATE] Recorded used video ID {video_id} (Total history: {len(used_ids)})")
    except Exception as e:
        print(f"[PEXELS WARNING] Failed to save {USED_VIDEOS_JSON}: {e}")

def check_exclusion(video):
    """動画が不適切キーワード（人物/医療/ジム/建物/CG等）を含んでいないか判定する"""
    url = video.get("url", "").lower()
    slug = url.split("/video/")[-1].rsplit("-", 1)[0] if "/video/" in url else url
    words = set(re.findall(r'[a-z0-9]+', slug.lower()))
    
    for ng in EXCLUSION_WORDS:
        if ng in words:
            return False, f"NG word '{ng}' in URL slug: '{slug}'"
            
    tags = video.get("tags", [])
    if isinstance(tags, list):
        for t in tags:
            tag_words = set(re.findall(r'[a-z0-9]+', str(t).lower()))
            for ng in EXCLUSION_WORDS:
                if ng in tag_words:
                    return False, f"NG word '{ng}' in tag: '{t}'"
                    
    return True, "OK"

def get_target_theme_and_sync():
    """
    台本テーマを選択し、test_output/current_theme.json に保存して後続パイプラインと同期する。
    （台本本文・タイトル・音声設定等は一切変更しない）
    """
    env_theme_id = os.environ.get('THEME_ID', '').strip()
    if env_theme_id:
        theme = get_theme_by_id(env_theme_id)
        print(f"[PEXELS DOWNLOAD] Using specified THEME_ID: {env_theme_id}")
    else:
        theme = select_next_theme()
        print(f"[PEXELS DOWNLOAD] Using current rotation theme: {theme.get('theme_id')}")

    if not theme:
        print("[PEXELS ERROR] Failed to determine theme.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    try:
        with open(CURRENT_THEME_JSON, 'w', encoding='utf-8') as f:
            json.dump(theme, f, ensure_ascii=False, indent=2)
        print(f"[PEXELS SYNC] Saved selected theme to {CURRENT_THEME_JSON}")
    except Exception as e:
        print(f"[PEXELS WARNING] Could not save current_theme.json: {e}")

    print(f"[PEXELS DOWNLOAD] Target theme: '{theme.get('theme_id')}' ({theme.get('title')})")
    print(f"[PEXELS DOWNLOAD] Narration: \"{theme.get('narration')}\"")
    return theme

def select_best_video_file(video):
    """動画からShortsに最適なMP4ファイルを選択する"""
    video_files = video.get('video_files', [])
    # 1. 縦型解像度（高さ1280以上）のmp4
    for vf in video_files:
        if vf.get('file_type') == 'video/mp4' and vf.get('height', 0) >= 1280:
            return vf
    # 2. HD mp4
    for vf in video_files:
        if vf.get('quality') == 'hd' and vf.get('file_type') == 'video/mp4':
            return vf
    # 3. 任意のmp4
    for vf in video_files:
        if vf.get('file_type') == 'video/mp4':
            return vf
    return None

def fetch_nature_background_video(output_file_path):
    """
    自然・癒し系キーワードプールから厳選された高品質な背景動画を取得する。
    """
    api_key = os.environ.get('PEXELS_API_KEY')
    if not api_key:
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
                api_key, _ = winreg.QueryValueEx(key, "PEXELS_API_KEY")
                os.environ["PEXELS_API_KEY"] = api_key
        except Exception:
            pass

    if not api_key:
        print("[PEXELS ERROR] PEXELS_API_KEY is not set.", file=sys.stderr)
        sys.exit(1)

    headers = {
        "Authorization": api_key
    }

    used_video_ids = load_used_video_ids()
    print(f"[PEXELS NATURE] Loaded {len(used_video_ids)} previously used video IDs.")

    # 検索クエリプールをシャッフルして多様性を確保
    queries = list(NATURE_QUERY_POOLS)
    random.shuffle(queries)

    chosen_file = None
    selected_video = None
    matched_query = None

    for q in queries:
        print(f"[PEXELS SEARCH] Searching nature query: '{q}' (portrait mode)...")
        url = f"https://api.pexels.com/videos/search?query={requests.utils.quote(q)}&per_page=15&orientation=portrait"

        try:
            res = requests.get(url, headers=headers, timeout=15)
            res.raise_for_status()
            data = res.json()
            videos = data.get('videos', [])

            if not videos:
                continue

            valid_candidates = []
            for v in videos:
                v_id = v.get('id')
                dur = v.get('duration', 0)

                # 条件1: 10秒以上の長さ
                if dur < 10:
                    continue

                # 条件2: 不適切動画（人物/医療/ジム/CG等）の除外
                is_ok, reason = check_exclusion(v)
                if not is_ok:
                    print(f"  [EXCLUDED] Video {v_id}: {reason}")
                    continue

                # 条件3: 過去使用動画の重複除外
                if v_id in used_video_ids:
                    print(f"  [DUPLICATE SKIPPED] Video {v_id} was recently used.")
                    continue

                # 条件4: 最適なMP4ファイルが存在するか
                vf = select_best_video_file(v)
                if not vf:
                    continue

                valid_candidates.append((v, vf))

            if valid_candidates:
                # 自然系として適切な候補の中からランダムに1本を選択
                selected_candidate = random.choice(valid_candidates)
                selected_video, chosen_file = selected_candidate
                matched_query = q
                print(f"[PEXELS MATCH] Selected nature video {selected_video.get('id')} from {len(valid_candidates)} valid candidates with query '{q}'!")
                break

        except Exception as e:
            print(f"[PEXELS WARNING] Search error for query '{q}': {e}. Trying next...")
            continue

    # フォールバック：万一全クエリで未使用動画が見つからなかった場合、過去ID制限を解除して自然系から再選定
    if not selected_video or not chosen_file:
        print("[PEXELS FALLBACK] All queries exhausted with unused IDs. Relaxing duplicate filter for nature videos...")
        for q in queries:
            url = f"https://api.pexels.com/videos/search?query={requests.utils.quote(q)}&per_page=15&orientation=portrait"
            try:
                res = requests.get(url, headers=headers, timeout=15)
                res.raise_for_status()
                videos = res.json().get('videos', [])
                valid_candidates = []
                for v in videos:
                    if v.get('duration', 0) >= 10 and check_exclusion(v)[0] and select_best_video_file(v):
                        valid_candidates.append((v, select_best_video_file(v)))
                if valid_candidates:
                    selected_video, chosen_file = random.choice(valid_candidates)
                    matched_query = q
                    break
            except Exception:
                continue

    if not selected_video or not chosen_file:
        print("[PEXELS ERROR] Failed to find any suitable nature video. Aborting.", file=sys.stderr)
        sys.exit(1)

    download_url = chosen_file.get('link')
    video_id = selected_video.get('id')
    video_url = selected_video.get('url')
    dur = selected_video.get('duration')
    w, h = chosen_file.get('width'), chosen_file.get('height')

    print(f"[PEXELS SUCCESS] Query: '{matched_query}'")
    print(f"[PEXELS SUCCESS] Video ID: {video_id}, Duration: {dur}s, Resolution: {w}x{h}")
    print(f"[PEXELS SUCCESS] Video URL: {video_url}")
    print("Downloading nature video from Pexels API...")

    res = requests.get(download_url, stream=True, timeout=30)
    res.raise_for_status()

    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    with open(output_file_path, 'wb') as f:
        for chunk in res.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    file_size = os.path.getsize(output_file_path)
    print(f"Download complete: {os.path.abspath(output_file_path)} ({file_size:,} bytes)")

    # 採用された動画IDを記録
    save_used_video_id(video_id)

def main():
    get_target_theme_and_sync()
    output_file_path = os.path.join(OUTPUT_DIR, 'pexels_test.mp4')
    fetch_nature_background_video(output_file_path)

if __name__ == '__main__':
    main()
