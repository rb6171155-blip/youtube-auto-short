import os
import sys
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# ==============================================================================
# アップロード公開設定スイッチ
# ==============================================================================
# ENABLE_SCHEDULED_PUBLISH:
#   False: 事前チェック用「限定公開（unlisted）」モード（予約公開 publishAt を無効化）
#   True : 本番運用用「24時間後予約公開（publishAt + private）」モード
ENABLE_SCHEDULED_PUBLISH = False

# デフォルトのプライバシーステータス（ENABLE_SCHEDULED_PUBLISH = False 時に適用）
DEFAULT_PRIVACY_STATUS = 'unlisted'
# ==============================================================================

CLIENT_ID = os.environ.get('YOUTUBE_CLIENT_ID')
CLIENT_SECRET = os.environ.get('YOUTUBE_CLIENT_SECRET')
REFRESH_TOKEN = os.environ.get('YOUTUBE_REFRESH_TOKEN')
PUBLISH_AT = os.environ.get('YOUTUBE_PUBLISH_AT', '')
PRIVACY_STATUS = os.environ.get('YOUTUBE_PRIVACY_STATUS', DEFAULT_PRIVACY_STATUS)
VIDEO_PATH = os.environ.get('VIDEO_PATH', os.path.join('test_output', 'shorts_test.mp4'))
VIDEO_TITLE = os.environ.get('YOUTUBE_VIDEO_TITLE', '医療法人 西田医院 #Shorts')
VIDEO_DESCRIPTION = os.environ.get('YOUTUBE_VIDEO_DESCRIPTION', '医療法人 西田医院公式 YouTube Shorts\n\n#西田医院 #リハビリ #介護 #医療 #Shorts')

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

def upload_video(youtube, file_path, publish_at=None, title=VIDEO_TITLE, description=VIDEO_DESCRIPTION, privacy_status=DEFAULT_PRIVACY_STATUS):
    if not os.path.exists(file_path):
        print(f"Error: Video file not found at {file_path}", file=sys.stderr)
        sys.exit(1)

    # 予約公開(publishAt)が指定されている場合、YouTube API仕様によりprivacyStatusは必ずprivateである必要がある
    if publish_at:
        privacy_status = 'private'

    print(f"Target video file: {file_path}")
    print(f"Target privacyStatus: {privacy_status}")
    if publish_at:
        print(f"Scheduled publish time (publishAt): {publish_at}")
    else:
        print("Scheduled publish (publishAt): Disabled (Instant Upload)")

    # #Shortsタグが含まれていることを確認
    if '#Shorts' not in title and '#shorts' not in title:
        title = f"{title} #Shorts"
    if '#Shorts' not in description and '#shorts' not in description:
        description = f"{description}\n\n#Shorts"

    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['Shorts', '西田医院', 'リハビリ', '介護', '医療']
        },
        'status': {
            'privacyStatus': privacy_status,
            'selfDeclaredMadeForKids': False
        }
    }

    # publishAt が明示指定された場合のみ追加
    if publish_at:
        body['status']['publishAt'] = publish_at

    try:
        media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype='video/mp4')
        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )

        print(f"Starting video upload to YouTube (privacyStatus: {privacy_status})...")
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
        print(f"Confirmed Privacy Status: {status_info.get('privacyStatus')}")
        if 'publishAt' in status_info:
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

    # スイッチフラグによるモード判定
    if ENABLE_SCHEDULED_PUBLISH:
        target_publish_at = PUBLISH_AT if PUBLISH_AT else None
        target_privacy_status = 'private'
        print("[MODE] Scheduled Publish Mode ACTIVE (publishAt enabled, privacyStatus: private)")
    else:
        target_publish_at = None
        target_privacy_status = PRIVACY_STATUS if PRIVACY_STATUS else DEFAULT_PRIVACY_STATUS
        print(f"[MODE] Unlisted Evaluation Mode ACTIVE (publishAt disabled, privacyStatus: {target_privacy_status})")

    upload_video(
        youtube=youtube,
        file_path=VIDEO_PATH,
        publish_at=target_publish_at,
        title=VIDEO_TITLE,
        description=VIDEO_DESCRIPTION,
        privacy_status=target_privacy_status
    )

if __name__ == '__main__':
    main()
