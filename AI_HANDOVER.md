# YouTube自動予約投稿プロジェクト 引き継ぎ資料

## プロジェクト基本情報
- プロジェクトルート: C:\Users\yuusu\.gemini\projects\youtube-auto-short
- GitHubリポジトリ: https://github.com/rb6171155-blip/youtube-auto-short.git
- デフォルトブランチ: main
- 初回コミットハッシュ: e722b40eb60656ccb959d0a5e520b5c460e64e0e

## 現在のステータスと実施済み作業
- Git初期化とリモートリポジトリ（origin）の設定が完了し、初回コミットをGitHubにpush済み。
- Google OAuth 2.0 Desktop App認証設定およびYouTube Data API v3の認証が完了。
- 認証情報とRefresh Tokenを含む token.json がプロジェクトルートに正常に作成済み。
- Pexels APIの疎通確認および動画ダウンロード用スクリプト（pexels_download.py）を作成済み。
- Pexels APIダウンロードテストを実行したが、環境変数 PEXELS_API_KEY が未設定のため処理を一時停止（想定通りの動作）。
- 動画編集（MoviePyなど）、YouTube自動アップロード、GitHub Actions workflowは未実装。
- GitHub Repository Secretsに以下の4項目が登録済みです（値は未記録）:
- PEXELS_API_KEY
- YOUTUBE_CLIENT_ID
- YOUTUBE_CLIENT_SECRET
- YOUTUBE_REFRESH_TOKEN。

## 重要な判断・制約・セキュリティ上の注意
- 機密情報（token.json、client_secret_*.json）およびキャッシュファイル（__pycache__/など）がGit管理下に入らないよう、.gitignore で厳重に除外しています。これらのファイルは絶対にGitHubにpushしないでください。
- APIキー、Client Secret、Refresh Tokenなどの具体的な秘密情報の値は、本ファイルを含むいかなるソースコードやドキュメントにも直接記録しないでください。
- Windows環境での認証ダイアログのストールを避けるため、GitHub連携の認証にはGitHub CLI（gh）のポータブル版を AppData\Local\Programs\gh-portable 配下に導入し、デバイスコード認証を利用して認証を紐付けました。

## 次にやるべき作業（最優先）
1. Windowsユーザー環境変数「PEXELS_API_KEY」に有効なPexelsのAPIキーを設定する。
2. C:\Users\yuusu\.gemini\projects\youtube-auto-short\pexels_download.py を実行し、test_output フォルダへテスト動画が正常にダウンロードされるか確認する。

