import os
import sys
import argparse
import requests

def download_video_from_pexels(query, output_dir="downloaded_videos", orientation="portrait", min_duration=10):
    """
    Windows環境変数 PEXELS_API_KEY から認証情報を安全に取得し、
    指定したテーマ（キーワード）の実写動画をPexelsからダウンロードする関数
    """
    api_key = os.environ.get("PEXELS_API_KEY")
    if not api_key:
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment")
            api_key, _ = winreg.QueryValueEx(key, "PEXELS_API_KEY")
            os.environ["PEXELS_API_KEY"] = api_key
        except Exception:
            pass

    if not api_key:
        print("エラー: Windowsの環境変数 'PEXELS_API_KEY' が設定されていません。", file=sys.stderr)
        return False

    os.makedirs(output_dir, exist_ok=True)
    print(f"検索テーマ: '{query}'")
    print("Pexels APIへ実写動画の検索リクエストを送信中...")

    headers = {
        "Authorization": api_key
    }

    search_url = f"https://api.pexels.com/videos/search?query={requests.utils.quote(query)}&per_page=10"
    if orientation:
        search_url += f"&orientation={orientation}"

    try:
        response = requests.get(search_url, headers=headers, timeout=15)
        if response.status_code == 401:
            print("エラー: PEXELS_API_KEY が無効です。", file=sys.stderr)
            return False
        response.raise_for_status()
        data = response.json()

        videos = data.get("videos", [])
        if not videos and orientation:
            print(f"指定の向き({orientation})で見つからなかったため、全動画から再検索します...")
            fallback_url = f"https://api.pexels.com/videos/search?query={requests.utils.quote(query)}&per_page=10"
            fb_res = requests.get(fallback_url, headers=headers, timeout=15)
            fb_res.raise_for_status()
            videos = fb_res.json().get("videos", [])

        if not videos:
            print(f"テーマ '{query}' に一致する動画は見つかりませんでした。", file=sys.stderr)
            return False

        selected_video = None
        for v in videos:
            if v.get("duration", 0) >= min_duration:
                selected_video = v
                break
        if not selected_video:
            selected_video = videos[0]

        video_id = selected_video.get("id")
        duration = selected_video.get("duration")
        video_files = selected_video.get("video_files", [])

        if not video_files:
            print("動画ファイルリンクが見つかりませんでした。", file=sys.stderr)
            return False

        chosen_file = None
        for vf in video_files:
            if vf.get("file_type") == "video/mp4" and vf.get("quality") == "hd":
                chosen_file = vf
                break
        if not chosen_file:
            for vf in video_files:
                if vf.get("file_type") == "video/mp4":
                    chosen_file = vf
                    break
        if not chosen_file:
            chosen_file = video_files[0]

        download_url = chosen_file.get("link")
        width = chosen_file.get("width")
        height = chosen_file.get("height")

        safe_query = "".join([c if c.isalnum() else "_" for c in query]).strip("_")
        output_filename = f"pexels_{safe_query}_{video_id}.mp4"
        output_path = os.path.join(output_dir, output_filename)

        print(f"動画選定完了: ID={video_id}, 長さ={duration}秒, 解像度={width}x{height}")
        print("動画のダウンロードを開始します...")

        video_res = requests.get(download_url, stream=True, timeout=30)
        video_res.raise_for_status()

        with open(output_path, "wb") as f:
            for chunk in video_res.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        file_size = os.path.getsize(output_path)
        print(f"ダウンロード完了: {os.path.abspath(output_path)} ({file_size:,} bytes)")
        return True

    except Exception as e:
        print(f"エラーが発生しました: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="Pexelsからテーマに応じた実写動画をダウンロードするスクリプト")
    parser.add_argument("query", nargs="?", default="nature", help="検索テーマ・キーワード")
    parser.add_argument("--dir", default="downloaded_videos", help="保存先ディレクトリ")
    parser.add_argument("--orientation", default="portrait", choices=["portrait", "landscape", "square", "all"], help="動画の向き")
    args = parser.parse_args()

    orient = None if args.orientation == "all" else args.orientation
    success = download_video_from_pexels(query=args.query, output_dir=args.dir, orientation=orient)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
