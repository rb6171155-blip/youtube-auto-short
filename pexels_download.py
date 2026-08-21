import os
import sys
import requests

PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY')
SEARCH_QUERY = 'aquarium'
OUTPUT_DIR = 'test_output'

def main():
    if not PEXELS_API_KEY:
        print("Error: PEXELS_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    url = f"https://api.pexels.com/videos/search?query={SEARCH_QUERY}&per_page=1"
    headers = {
        "Authorization": PEXELS_API_KEY
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        videos = data.get('videos', [])
        if not videos:
            print(f"No videos found for query: {SEARCH_QUERY}", file=sys.stderr)
            sys.exit(1)

        video = videos[0]
        video_files = video.get('video_files', [])
        if not video_files:
            print("No video files found in the result.", file=sys.stderr)
            sys.exit(1)

        download_url = video_files[0].get('link')
        if not download_url:
            print("No download link available for the video.", file=sys.stderr)
            sys.exit(1)

        output_file_path = os.path.join(OUTPUT_DIR, 'pexels_test.mp4')
        print("Downloading video from Pexels API...")

        video_response = requests.get(download_url, stream=True)
        video_response.raise_for_status()

        with open(output_file_path, 'wb') as f:
            for chunk in video_response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        file_size = os.path.getsize(output_file_path)
        print(f"Download complete: {os.path.abspath(output_file_path)}")
        print(f"Video file size: {file_size} bytes")

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
