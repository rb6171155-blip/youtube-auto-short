import os
import sys
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

CLIENT_ID = os.environ.get('YOUTUBE_CLIENT_ID')
CLIENT_SECRET = os.environ.get('YOUTUBE_CLIENT_SECRET')
REFRESH_TOKEN = os.environ.get('YOUTUBE_REFRESH_TOKEN')

def get_authenticated_service():
    if not CLIENT_ID or not CLIENT_SECRET or not REFRESH_TOKEN:
        print("Error: Missing required YouTube OAuth credentials in environment variables.", file=sys.stderr)
        sys.exit(1)

    try:
        credentials = Credentials(
            token=None,
            refresh_token=REFRESH_TOKEN,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            scopes=["https://www.googleapis.com/auth/youtube.upload"]
        )

        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        return build('youtube', 'v3', credentials=credentials)
    except Exception as e:
        print(f"Error authenticating with YouTube API: {e}", file=sys.stderr)
        sys.exit(1)

def upload_video(youtube, file_path):
    if not os.path.exists(file_path):
        print(f"Error: Video file not found at {file_path}", file=sys.stderr)
        sys.exit(1)

    body = {
        'snippet': {
            'title': 'Test Upload Video',
            'description': 'This is a test upload via YouTube Data API v3 in GitHub Actions.',
            'tags': ['test', 'api']
        },
        'status': {
            'privacyStatus': 'private'
        }
    }

    try:
        media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype='video/mp4')
        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )

        print("Starting video upload to YouTube...")
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Uploaded {int(status.progress() * 100)}%")

        video_id = response.get('id')
        print(f"Upload successful. Video ID: {video_id}")
        return video_id
    except HttpError as e:
        print(f"YouTube API HTTP Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error during upload: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    video_path = os.path.join('test_output', 'pexels_test.mp4')
    youtube = get_authenticated_service()
    upload_video(youtube, video_path)

if __name__ == '__main__':
    main()
