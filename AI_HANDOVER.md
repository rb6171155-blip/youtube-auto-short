# YouTube自動予約投稿プロジェクト 引き継ぎ資料

## プロジェクト基本情報
- プロジェクトルート: C:\Users\yuusu\.gemini\projects\youtube-auto-short
- GitHubリポジトリ: https://github.com/rb6171155-blip/youtube-auto-short.git
- デフォルトブランチ: main

## 現在のステータスと実施済み作業
- Git初期化とリモートリポジトリ（origin）の設定が完了し、ワークフロー定義およびテストスクリプトをGitHubにpush済み。
- Google OAuth 2.0 Desktop App認証設定およびYouTube Data API v3の認証が完了。
- 認証情報とRefresh Tokenを含む token.json がローカルのプロジェクトルートに作成済み（Git除外）。
- GitHub Repository Secretsに以下の4項目が登録済み（値は未記録）：
  - PEXELS_API_KEY
  - YOUTUBE_CLIENT_ID
  - YOUTUBE_CLIENT_SECRET
  - YOUTUBE_REFRESH_TOKEN
- Pexels APIの動画素材取得スクリプト（pexels_download.py）を実装済み（GitHub Actions上で動作確認済み）。
- YouTube Data API v3を使用した非公開アップロード用スクリプト（youtube_upload.py）を実装済み（GitHub Actions上で動画ID: Y4MgbCYxzcI としてアップロード成功を確認済み）。
- ffmpegを使用したShorts向け縦型9:16変換スクリプト（shorts_convert.py）を実装済み。GitHub Actions（.github/workflows/test_shorts_convert.yml）上で元動画（960x540）から中央クロップにより1080x1920（アスペクト比0.5625）への変換および出力ファイルの検証が完全に成功することを確認済み。
- 字幕、音声、AI生成、複数素材結合、cronによる本番自動予約投稿ワークフローは未実装。

## 今回の作成・変更ファイル
- shorts_convert.py（新規作成：ffmpeg/ffprobeを利用した9:16 Shorts縦型変換および解像度検証スクリプト）
- .github/workflows/test_shorts_convert.yml（新規作成：Pexels動画取得から9:16変換・検証までを実行するテストワークフロー）
- AI_HANDOVER.md（更新：9:16変換テストの成功結果および最新ステータスを記録）

## 重要な判断・制約・セキュリティ上の注意
- 最終運用方針として「ローカルPCの電源がOFFでもGitHub Actions単体で自動実行される構成」を完全に実証しています。ローカルPCへの不要な秘密情報の追加登録は行わず、GitHub Repository Secretsを活用しています。
- 機密情報（token.json、client_secret_*.json）および生成動画ファイル（test_output/、*.mp4）がGit管理下に入らないよう、.gitignore で厳重に除外しています。これらのファイルは絶対にGitHubにpushしないでください。
- APIキー、Client Secret、Refresh Tokenなどの具体的な秘密情報の値は、本ファイルを含むいかなるソースコードやドキュメントにも直接記録しないでください。
- GitHub ActionsのUbuntu runner（ubuntu-latest）では、ffmpeg/ffprobeを明示的に apt インストールするステップを含めることで、確実に動画変換処理が動作する設計としています。
- 既存のPexels取得処理およびYouTubeアップロード処理は壊さず正常に維持されています。

## 次にやるべき作業（最優先）
1. YouTubeアップロード処理（youtube_upload.py）を拡張し、生成された9:16 Shorts動画（test_output/shorts_test.mp4）を対象とし、タイトル・説明文・#Shortsタグおよび予約投稿日時（status.publishAt）を設定してアップロードできる機能を実装する。
2. GitHub Actions上で、Pexels取得 → 9:16変換 → YouTube予約投稿（指定日時で非公開・予約公開）までの一連の流れをテストする。
