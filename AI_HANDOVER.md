# YouTube自動予約投稿プロジェクト 引き継ぎ資料

## プロジェクト基本情報
- プロジェクトルート: C:\Users\yuusu\.gemini\projects\youtube-auto-short
- GitHubリポジトリ: https://github.com/rb6171155-blip/youtube-auto-short.git
- デフォルトブランチ: main

## 現在のステータスと実施済み作業
- Git初期化とリモートリポジトリ（origin）の設定が完了し、初回コミットおよびワークフロー定義をGitHubにpush済み。
- Google OAuth 2.0 Desktop App認証設定およびYouTube Data API v3の認証が完了。
- 認証情報とRefresh Tokenを含む token.json がローカルのプロジェクトルートに正常に作成済み。
- GitHub Repository Secretsに以下の4項目が登録済み（値は未記録）：
  - PEXELS_API_KEY
  - YOUTUBE_CLIENT_ID
  - YOUTUBE_CLIENT_SECRET
  - YOUTUBE_REFRESH_TOKEN
- Pexels APIの疎通確認および動画ダウンロード用スクリプト（pexels_download.py）を作成済み。
- GitHub Actionsワークフロー（.github/workflows/test_pexels.yml）を作成し、GitHub Actions上でSecrets.PEXELS_API_KEYを利用してPexels APIからmp4動画素材を自動取得するテストを実行。正常にダウンロード完了（約52.7MB）することを確認済み。
- 動画編集（MoviePyなど）、YouTube自動アップロード、本番用自動予約投稿ワークフローは未実装。

## 重要な判断・制約・セキュリティ上の注意
- 最終運用方針として「ローカルPCの電源がOFFでもGitHub Actions単体で自動実行される構成」を採用しています。ローカルPCへの不要な秘密情報の追加登録は行わず、GitHub Repository Secretsを活用します。
- 機密情報（token.json、client_secret_*.json）および生成動画ファイル（test_output/、*.mp4）がGit管理下に入らないよう、.gitignore で厳重に除外しています。これらのファイルは絶対にGitHubにpushしないでください。
- APIキー、Client Secret、Refresh Tokenなどの具体的な秘密情報の値は、本ファイルを含むいかなるソースコードやドキュメントにも直接記録しないでください。
- GitHub CLI（gh）には「workflow」スコープを含む認証設定が完了しており、GitHub ActionsワークフローのGit pushおよび管理が可能です。

## 次にやるべき作業（最優先）
1. YouTube Data API v3を使用して動画をアップロード（および予約投稿日時の設定）を行うための最小限のPythonスクリプトを実装する。
2. GitHub ActionsからSecrets（YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN）を渡し、YouTubeへのテストアップロード（限定公開または非公開での疎通確認）を検証する。
