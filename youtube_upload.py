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
PUBLISH_AT = os.environ.get('YOUTUBE_PUBLISH_AT')
VIDEO_PATH = os.environ.get('VIDEO_PATH', os.path.join('test_output', 'shorts_test.mp4'))
VIDEO_TITLE = os.environ.get('YOUTUBE_VIDEO_TITLE', 'Test Shorts Scheduled Upload #Shorts')
VIDEO_DESCRIPTION = os.environ.get('YOUTUBE_VIDEO_DESCRIPTION', 'Test scheduled Shorts upload via GitHub Actions. #Shorts')

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

def upload_video(youtube, file_path, publish_at, title=VIDEO_TITLE, description=VIDEO_DESCRIPTION):
    if not os.path.exists(file_path):
        print(f"Error: Video file not found at {file_path}", file=sys.stderr)
        sys.exit(1)

    if not publish_at:
        print("Error: YOUTUBE_PUBLISH_AT environment variable is required (ISO 8601 UTC format).", file=sys.stderr)
        sys.exit(1)

    print(f"Target video file: {file_path}")
    print(f"Scheduled publish time (publishAt): {publish_at}")

    # #Shortsタグが含まれていることを確認
    if '#Shorts' not in title and '#shorts' not in title:
        title = f"{title} #Shorts"
    if '#Shorts' not in description and '#shorts' not in description:
        description = f"{description}\n\n#Shorts"

    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['Shorts', 'aquarium', 'relaxation']
        },
        'status': {
            'privacyStatus': 'private',
            'publishAt': publish_at,
            'selfDeclaredMadeForKids': False
        }
    }

    try:
        media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype='video/mp4')
        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )

        print("Starting scheduled video upload to YouTube...")
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Uploaded {int(status.progress() * 100)}%")

        video_id = response.get('id')
        status_info = response.get('status', {})
        snippet_info = response.get('snippet', {})

        print(f"Upload successful. Video ID: {video_id}")
        print(f"Uploaded Video Title: {snippet_info.get('title')}")
        print(f"Privacy Status: {status_info.get('privacyStatus')}")
        print(f"Confirmed publishAt: {status_info.get('publishAt')}")

        return response
    except HttpError as e:
        print(f"YouTube API HTTP Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error during upload: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    youtube = get_authenticated_service()
    upload_video(youtube, VIDEO_PATH, PUBLISH_AT, VIDEO_TITLE, VIDEO_DESCRIPTION)

if __name__ == '__main__':
    main()
