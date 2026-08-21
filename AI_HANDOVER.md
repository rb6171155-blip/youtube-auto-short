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
- Pexels APIの動画素材取得スクリプト（pexels_download.py）を実装し、軽量動画（SD品質等）を選択してダウンロードするよう最適化済み。
- YouTube Data API v3を使用した非公開アップロード用スクリプト（youtube_upload.py）を実装済み。
- GitHub Actionsワークフロー（.github/workflows/test_youtube_upload.yml）を実行し、GitHub Actions上からSecretsを利用してPexels動画取得およびYouTubeへの非公開アップロード（動画ID: Y4MgbCYxzcI）が完全に成功することを確認済み。
- 本番用の動画自動編集（字幕・音声・アスペクト比変換等）および自動予約投稿スケジュール管理は未実装。

## 今回の作成・変更ファイル
- youtube_upload.py（新規作成：YouTube Data API v3 非公開アップロードスクリプト）
- .github/workflows/test_youtube_upload.yml（新規作成：Pexels取得からYouTubeアップロードまでを行うテストワークフロー）
- pexels_download.py（更新：テスト用に軽量動画ファイルを優先選択するロジックを追加）
- .github/workflows/test_pexels.yml（更新：手動実行のみにトリガー変更）

## 重要な判断・制約・セキュリティ上の注意
- 最終運用方針として「ローカルPCの電源がOFFでもGitHub Actions単体で自動実行される構成」を完全に実証しました。ローカルPCへの不要な秘密情報の追加登録は行わず、GitHub Repository Secretsを活用しています。
- 機密情報（token.json、client_secret_*.json）および生成動画ファイル（test_output/、*.mp4）がGit管理下に入らないよう、.gitignore で厳重に除外しています。これらのファイルは絶対にGitHubにpushしないでください。
- APIキー、Client Secret、Refresh Tokenなどの具体的な秘密情報の値は、本ファイルを含むいかなるソースコードやドキュメントにも直接記録しないでください。
- YouTube APIのアップロードは「非公開（private）」にて動作確認済みです。

## 次にやるべき作業（最優先）
1. ショート動画（縦型 9:16）向けに動画を自動加工・編集する処理（MoviePyやffmpeg等を用いたクロップ・リサイズ・テキストオーバーレイ等の最小構成）を実装する。
2. YouTubeアップロード時に予約投稿日時（publishAt）およびショート動画向けメタデータ（#Shortsタグなど）を設定できる拡張を実装する。
