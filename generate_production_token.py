import os
import sys
import json
import shutil
import subprocess
from google_auth_oauthlib.flow import InstalledAppFlow
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# クライアントシークレットファイルの選択（client_secret_new.json を最優先）
CLIENT_SECRET_FILE = os.path.join(BASE_DIR, 'client_secret_new.json')
if not os.path.exists(CLIENT_SECRET_FILE):
    CLIENT_SECRET_FILE = os.path.join(BASE_DIR, 'client_secret.json')

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
TOKEN_FILE = os.path.join(BASE_DIR, 'token_verified.json')
GH_EXE = r"C:\Users\yuusu\AppData\Local\Programs\gh-portable\bin\gh.exe"
REPO = "rb6171155-blip/youtube-auto-short"

def main():
    print("=" * 60)
    print(" YouTube OAuth In-Production Permanent Token Generator ")
    print("=" * 60)

    if not os.path.exists(CLIENT_SECRET_FILE):
        print(f"Error: OAuth Client JSON file not found at {CLIENT_SECRET_FILE}", file=sys.stderr)
        sys.exit(1)

    with open(CLIENT_SECRET_FILE, 'r', encoding='utf-8') as f:
        cs_data = json.load(f)
    client_info = cs_data.get('installed', cs_data.get('web', {}))
    client_id = client_info.get('client_id', '')
    client_secret = client_info.get('client_secret', '')
    project_id = client_info.get('project_id', '')

    print(f"Using Client File : {os.path.basename(CLIENT_SECRET_FILE)}")
    print(f"Project ID        : {project_id}")
    print(f"Client ID Prefix  : {client_id[:30]}...")
    print(f"Requested Scope   : {SCOPES[0]}")
    print(f"Destination       : {TOKEN_FILE}")
    print("-" * 60)

    # 既存トークンのバックアップ
    if os.path.exists(TOKEN_FILE):
        backup_path = os.path.join(BASE_DIR, 'token_verified.json.bak')
        shutil.copy2(TOKEN_FILE, backup_path)
        print(f"Existing token backed up to: token_verified.json.bak")

    print("\n[Step 1] Launching OAuth 2.0 Authorization Flow...")
    print("ブラウザが開きます。YouTubeチャンネルの管理者Googleアカウントでログインし、アクセスを許可してください。\n")

    # prompt='consent' と access_type='offline' を明示して確実に新しいRefresh Tokenを取得
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    credentials = flow.run_local_server(
        port=0,
        open_browser=True,
        prompt='consent',
        access_type='offline'
    )

    # 認証情報を token_verified.json に保存
    with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
        f.write(credentials.to_json())
    print("\n[Step 1 Complete] Token file written to token_verified.json successfully.")

    # Step 2: 動作検証
    print("\n[Step 2] Verifying new Refresh Token with YouTube Data API v3...")
    with open(TOKEN_FILE, 'r', encoding='utf-8') as f:
        tok_data = json.load(f)
    refresh_token = tok_data.get('refresh_token')

    if not refresh_token:
        print("Error: No refresh_token found in generated token file.", file=sys.stderr)
        sys.exit(1)

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES
    )
    request = google.auth.transport.requests.Request()
    creds.refresh(request)
    print("Token Refresh Test: SUCCESS (Permanent Access Token Generated)")

    youtube = build('youtube', 'v3', credentials=creds)
    print("YouTube API Client Initialization: SUCCESS")

    # Step 3: GitHub Secrets 自動同期
    print("\n[Step 3] Syncing Secrets with GitHub Repository: " + REPO)
    if os.path.exists(GH_EXE):
        subprocess.run([GH_EXE, "secret", "set", "YOUTUBE_CLIENT_ID", "--repo", REPO, "--body", client_id], check=True)
        subprocess.run([GH_EXE, "secret", "set", "YOUTUBE_CLIENT_SECRET", "--repo", REPO, "--body", client_secret], check=True)
        subprocess.run([GH_EXE, "secret", "set", "YOUTUBE_REFRESH_TOKEN", "--repo", REPO, "--body", refresh_token], check=True)
        print("GitHub Secrets (YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN) updated successfully!")
    else:
        print("Note: gh.exe not found at standard path. Please update GitHub Secrets manually.")

    # Step 4: 結果表示
    print("\n" + "=" * 60)
    print(" REFRESH TOKEN STRING FOR GITHUB SECRETS ")
    print("=" * 60)
    print(refresh_token)
    print("=" * 60)

if __name__ == '__main__':
    main()
