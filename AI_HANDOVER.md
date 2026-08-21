# YouTube自動予約投稿プロジェクト 引き継ぎ資料

## プロジェクト基本情報
- プロジェクトルート: C:\Users\yuusu\.gemini\projects\youtube-auto-short
- GitHubリポジトリ: https://github.com/rb6171155-blip/youtube-auto-short.git
- デフォルトブランチ: main

## 現在のステータスと実施済み・完成済み機能
1. Pexels API動画取得（pexels_download.py）：GitHub Actions上でPexels APIから素材を取得・ダウンロード可能。
2. ffmpegによる9:16 Shorts縦型変換（shorts_convert.py）：中央クロップおよび1080x1920（アスペクト比 0.5625）への変換・検証が完了。
3. YouTube OAuth 2.0認証（YouTube Data API v3）：GitHub Secrets経由でのアクセストークン自動リフレッシュが完了。
4. YouTube予約投稿・Shortsメタデータ設定（youtube_upload.py）：生成された9:16 Shorts動画を対象とし、タイトル・説明文・#Shortsタグ・非公開設定（privacyStatus: private）・指定未来日時の予約公開（publishAt）を設定したアップロードが完了。
5. GitHub Actions単体自動実行：ローカルPCの電源OFF状態でもGitHub Actions単体で「Pexels取得 → 9:16変換 → YouTube予約投稿」の全工程が完了することを実証済み。

## 今回の作成・変更ファイルおよびテスト結果
- 作成・変更ファイル：
  - youtube_upload.py（更新：予約投稿日時 publishAt および Shorts向けメタデータ設定機能を追加）
  - .github/workflows/test_scheduled_upload.yml（新規作成：Pexels取得 → 9:16変換 → YouTube予約投稿までの一連のテストワークフロー）
  - AI_HANDOVER.md（更新：最新のテスト結果および進捗を記録）
- GitHub Actionsテスト結果：
  - ワークフロー：Test Scheduled Shorts Upload
  - Run ID: 32440001407
  - 結果：成功（Success / 実行時間: 1分52秒）
  - アップロード動画ID: 3S7BUH60FFk
  - 予約公開設定日時（publishAt）: 2026-08-22T02:30:54Z（UTC / 実行日時の24時間後）
  - 公開状態（privacyStatus）: private
  - 動画タイトル: Test Shorts Scheduled Upload #Shorts

## 重要な判断・制約・セキュリティ上の注意
- 最終運用方針として「ローカルPCの電源がOFFでもGitHub Actions単体で自動実行される構成」を完全に実証しています。ローカルPCへの不要な秘密情報の追加登録は行わず、GitHub Repository Secretsを活用しています。
- 機密情報（token.json、client_secret_*.json）および生成動画ファイル（test_output/、*.mp4）がGit管理下に入らないよう、.gitignore で厳重に除外しています。これらのファイルは絶対にGitHubにpushしないでください。
- APIキー、Client Secret、Refresh Tokenなどの具体的な秘密情報の値は、本ファイルを含むいかなるソースコードやドキュメントにも直接記録しないでください。
- YouTube APIのアップロードは誤公開を防ぐため、常に「非公開（private）」かつ安全な未来日時を指定する「予約公開（publishAt）」で管理されています。
- テスト用ワークフローは不要な自動実行によるYouTube APIクォータ消費を防ぐため、トリガーを `workflow_dispatch`（手動実行）に設定しています。

## 次にやるべき作業（最優先）
1. 動画へのテキストオーバーレイ・タイトル合成処理（ffmpegのdrawtextフィルタ等を用いたShorts動画のコンテンツ品質向上）の実装。
2. 毎日決まった時間（例: 毎日午前9時など）に自動で動画生成から予約投稿までを完結させる本番用cronワークフロー（scheduleトリガー）の設計・実装。
