# YouTube自動予約投稿プロジェクト 引き継ぎ資料

## プロジェクト基本情報
- プロジェクトルート: C:\Users\yuusu\.gemini\projects\youtube-auto-short
- GitHubリポジトリ: https://github.com/rb6171155-blip/youtube-auto-short.git
- デフォルトブランチ: main

## 現在のステータスと完成済み機能（本番自動化完了）
1. Pexels API動画取得（pexels_download.py）：GitHub Actions上でPexels APIから素材を取得・ダウンロード可能。
2. ffmpegによる9:16 Shorts縦型変換（shorts_convert.py）：中央クロップおよび1080x1920（アスペクト比 0.5625）への変換・検証が完了。
3. YouTube OAuth 2.0認証（YouTube Data API v3）：GitHub Secrets経由でのアクセストークン自動リフレッシュが完了。
4. YouTube予約投稿・Shortsメタデータ設定（youtube_upload.py）：環境変数による本番タイトル・説明文・#Shortsタグ・非公開設定（privacyStatus: private）・指定未来日時の予約公開（publishAt）の設定に対応。
5. 本番用GitHub Actions自動投稿ワークフロー（.github/workflows/production_auto_post.yml）：
   - スケジュール設定：毎日 日本時間(JST) 午前09:00 / 協定世界時(UTC) 午前00:00 に自動実行（cron: '0 0 * * *'）
   - 手動実行（workflow_dispatch）にも対応
   - PC電源OFF状態でもGitHub Actions単体で「素材取得 → 9:16変換 → YouTube予約投稿」の全パイプラインが完全自動実行されます。

## 本番ワークフロー手動実行テスト結果
- ワークフロー名：Daily Auto Post Shorts to YouTube (.github/workflows/production_auto_post.yml)
- Run ID: 32444314557
- 実行結果：成功（Success / 実行時間: 1分56秒）
- アップロード動画ID: RZUFYXhnrCQ
- 動画タイトル: Daily Relaxation Aquarium Moments #Shorts
- 公開状態（privacyStatus）: private
- 予約公開設定日時（publishAt）: 2026-08-22T03:44:02Z（UTC / 実行日時の24時間後）

## 重要な判断・制約・セキュリティ上の注意
- 最終運用方針として「ローカルPCの電源がOFFでもGitHub Actions単体で自動実行される構成」を完全に実証・構築完了しました。ローカルPCへの不要な秘密情報の追加登録は行わず、GitHub Repository Secretsを活用しています。
- 機密情報（token.json、client_secret_*.json）および生成動画ファイル（test_output/、*.mp4）がGit管理下に入らないよう、.gitignore で厳重に除外しています。これらのファイルは絶対にGitHubにpushしないでください。
- APIキー、Client Secret、Refresh Tokenなどの具体的な秘密情報の値は、本ファイルを含むいかなるソースコードやドキュメントにも直接記録しないでください。
- YouTube APIのアップロードは誤公開を防ぐため、常に「非公開（private）」かつ安全な未来日時を指定する「予約公開（publishAt）」で管理されています。
- 1回のワークフロー実行につき動画1本のみを生成・投稿する安全設計となっています。

## 次に必要な作業（今後の拡張案）
1. 動画へのテキストオーバーレイ・字幕・BGM合成等のコンテンツ品質向上処理の追加（必要に応じて実装）。
2. 本番自動投稿の定期的な稼働確認（GitHub Actionsの実行履歴およびYouTube Studioでの予約投稿状況の確認）。
