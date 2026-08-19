import os
from google_auth_oauthlib.flow import InstalledAppFlow

CLIENT_SECRET_FILE = 'client_secret_587509058010-cndh0456dr40620i0tddqe6cjlkp0fgk.apps.googleusercontent.com.json'
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
TOKEN_FILE = 'token.json'

def main():
    if not os.path.exists(CLIENT_SECRET_FILE):
        print(f"Error: {CLIENT_SECRET_FILE} not found.")
        return

    # OAuth 2.0 認証フローを開始
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)

    # 認証情報をtoken.jsonに保存
    # セキュリティ要件に基づき、リフレッシュトークンなどの認証情報は画面やログに出力しません。
    with open(TOKEN_FILE, 'w') as f:
        f.write(credentials.to_json())
    
    print("Authentication successful. token.json has been created.")

if __name__ == '__main__':
    main()
