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
5. 本番用GitHub Actions自動投稿ワークフロー（.github/workflows/production_auto_post.yml）：毎日JST 09:00（UTC 00:00）に自動起動（cron: '0 0 * * *'）。※既存の本番パイプラインは安全に維持されています。
6. 疎結合AI音声ナレーションモジュール（voice_generator.py）：
   - 将来的にGoogle Cloud TTSやAzure等へ差し替え可能な汎用インターフェース（generate_voice）。
   - ja-JP-NanamiNeural（女性・話速 -5%）による落ち着いた温かみのある医療・介護ナレーション。
   - 失敗時にプロセスを停止させず安全にフォールバックを促す設計。
7. 確定済み21テーマ シナリオ定義データ（themes.py / M2完了）：
   - 7カテゴリー（理念、外来リハ、通所リハ、通所介護、ISR、レッドコード、小規模多機能）各3テーマ＝計21テーマを完全登録。
   - ナレーション原稿（聴覚用：完全文）と字幕原稿（視覚用：短文キーワード）を完全分離。
   - M1のDEFAULT_THEME（テーマ1-1：痛みの先にある生活）と完全な後方互換性を保持。
8. ナレーション・字幕・BGM統合動画生成パイプライン（generate_shorts_pipeline.py / shorts_editor.py）：
   - ナレーション主音声（volume=1.0）と控えめなアンビエントBGM（volume=0.06）のプロ品質ミキシング。
   - TTS失敗時の自動フォールバック（字幕＋BGMモードへ自動切り替え、動画生成・予約投稿を100%完遂）。
   - YouTube Shortsの右側UIと干渉しない幅800px（左右マージン140px）のセーフエリア対応角丸半透明ボックス。

## M1テスト結果（代表テーマ1-1）
- ワークフロー名：Test TTS Narration Video Pipeline (.github/workflows/test_tts_video.yml)
- Run ID：32457139693（実行時間: 2分30秒 / Success）
- 成果物（GitHub Artifacts）：[tts-video-completed.zip](https://github.com/rb6171155-blip/youtube-auto-short/actions/runs/32457139693/artifacts/9437674162)

## M2テスト結果（21テーマ登録）
- Python構文チェックおよび21テーマ・7カテゴリーのデータ完全性検証：成功
- DEFAULT_THEME互換性確認：成功

## 重要な判断・制約・セキュリティ上の注意
- 完全無料運用を絶対条件とし、有料API・課金サービス・不要な外部API呼び出しを一切排除。
- 既存の本番自動投稿ワークフロー（production_auto_post.yml）およびYouTubeアップロード処理は一切変更せず維持されています。
- 多重フォールバック設計により、外部TTSサービスの障害時でも自動投稿パイプライン全体が停止しない耐障害性を確保しています。
- 機密情報（token.json、client_secret_*.json）および生成動画ファイルは .gitignore で厳重に除外されています。

## 次に必要な作業（M3）
1. 確定済み21テーマを日替わり・ランダム等で選択・ローテーションする仕組みの確認。
2. 既存の本番自動投稿ワークフロー（production_auto_post.yml）への安全な接続準備（ユーザー承認後に実施）。
