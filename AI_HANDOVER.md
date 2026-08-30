# YouTube自動予約投稿プロジェクト 引き継ぎ資料 (AI_HANDOVER.md)

## プロジェクト基本情報
- プロジェクトルート: C:\Users\yuusu\.gemini\projects\youtube-auto-short
- GitHubリポジトリ: https://github.com/rb6171155-blip/youtube-auto-short.git
- デフォルトブランチ: main
- Google Cloud Project: youtube-auto-short-production (Project Number: 1012793477083)
- ドメイン所有権証明: https://yuusuikan.com/ (Verified)
- OAuth Publishing Status: In Production (本番環境・無期限トークン仕様)

## システム全体像
```text
GitHub Actions (毎日JST 09:00 / cron: '0 0 * * *')
  ↓
1. Pexels APIよりテーマ別動画素材の取得 (pexels_download.py)
  ↓
2. 9:16 (1080x1920) Shortsフォーマット変換 (shorts_convert.py)
  ↓
3. テーマローテーション・ナレーション音声生成 (themes.py / voice_generator.py - ja-JP-NanamiNeural -5%)
  ↓
4. 文単位タイムスタンプに完全同期したBudouX字幕・BGM合成 (generate_shorts_pipeline.py / shorts_editor.py)
  ↓
5. 15秒Shorts完成動画生成 (test_output/shorts_final.mp4)
  ↓
6. Google OAuth 2.0 In-Production Refresh Token による認証 (youtube_upload.py)
  ↓
7. YouTube Data API v3 による動画アップロード + publishAt による24時間後予約公開
  ↓
8. 成功時のみ state/theme_state.json を Git Commit & Push して自動確定
```

## 認証・Secrets構成
- PEXELS_API_KEY: Pexels API動画取得用キー
- YOUTUBE_CLIENT_ID: OAuth 2.0 クライアントID (Desktop App)
- YOUTUBE_CLIENT_SECRET: OAuth 2.0 クライアントシークレット
- YOUTUBE_REFRESH_TOKEN: In-Production 無期限Refresh Token (Scope: `https://www.googleapis.com/auth/youtube.upload`)

## 動作確認済みコマンド
- 本番トークン再生成＆GitHub Secrets自動同期: `py generate_production_token.py`
- OAuth認証テスト: `gh workflow run test_youtube_auth.yml --repo rb6171155-blip/youtube-auto-short`
- 本番予約投稿ワークフロー手動実行: `gh workflow run production_auto_post.yml --repo rb6171155-blip/youtube-auto-short`
