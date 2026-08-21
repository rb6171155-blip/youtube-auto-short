# YouTube自動予約投稿プロジェクト 引き継ぎ資料

## プロジェクト基本情報
- プロジェクトルート: C:\Users\yuusu\.gemini\projects\youtube-auto-short
- GitHubリポジトリ: https://github.com/rb6171155-blip/youtube-auto-short.git
- デフォルトブランチ: main

## 現在のステータスと完成済み機能
1. Pexels API動画取得（pexels_download.py）：GitHub Actions上でPexels APIから素材を取得・ダウンロード可能。
2. ffmpegによる9:16 Shorts縦型変換（shorts_convert.py）：中央クロップおよび1080x1920（アスペクト比 0.5625）への変換・検証が完了。
3. YouTube OAuth 2.0認証（YouTube Data API v3）：GitHub Secrets経由でのアクセストークン自動リフレッシュが完了。
4. YouTube予約投稿・Shortsメタデータ設定（youtube_upload.py）：環境変数による本番タイトル・説明文・#Shortsタグ・非公開設定（privacyStatus: private）・指定未来日時の予約公開（publishAt）の設定に対応。
5. 確定済み21テーマ シナリオ定義データ（themes.py）：
   - 7カテゴリー（理念、外来リハ、通所リハ、通所介護、ISR、レッドコード、小規模多機能）各3テーマ＝計21テーマを完全登録。
   - ナレーション原稿（聴覚用：完全文）と字幕原稿（視覚用：短文キーワード）を完全分離。
   - select_next_theme() による読み込みと commit_theme_state() による投稿成功時確定保存。
6. ナレーション・字幕・BGM統合動画生成パイプライン（generate_shorts_pipeline.py / shorts_editor.py / voice_generator.py）：
   - ja-JP-NanamiNeural（話速 -5%）による高品質ナレーション。
   - ナレーション主音声（volume=1.0）と控えめなアンビエントBGM（volume=0.06）のプロ品質ミキシング。
   - TTS失敗時の自動フォールバック（字幕＋BGMモードへ自動切り替え、動画生成・予約投稿を100%完遂）。
7. 本番自動投稿ワークフロー（.github/workflows/production_auto_post.yml）：
   - 毎日JST 09:00（UTC 00:00）の定時自動実行（cron: '0 0 * * *'）および手動実行（workflow_dispatch / theme_id 指定可能）。
   - concurrency による同時実行防止。
   - 投稿成功時（if: success()）のみ state/theme_state.json を Git Commit & Push して自動ローテーションを確定。

## テスト状況
- ローカル単体テスト：全項目合格
- テスト投稿準備：完了（ユーザーの実行承認待ち）
