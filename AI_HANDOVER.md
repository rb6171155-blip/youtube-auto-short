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
5. 本番用GitHub Actions自動投稿ワークフロー（.github/workflows/production_auto_post.yml）：毎日JST 09:00（UTC 00:00）に自動起動（cron: '0 0 * * *'）。
6. Shorts字幕・角丸半透明ボックス・BGM合成モジュール（shorts_editor.py）：
   - Pillowによる高品質な日本語フォント（Noto Sans JP Bold）描画
   - 画面中央〜下部に清潔感・安心感のあるダークネイビー半透明角丸ボックス配置
   - 15秒間で4シーンの字幕切り替え
   - 著作権フリー・安全な穏やかBGM（音量控えめ、末尾フェードアウト）の自動合成
   - 代表シーンのプレビュー静止画自動抽出

## 最新のテスト結果（試作動画 第1弾）
- ワークフロー名：Test Shorts Editor Subtitle and BGM (.github/workflows/test_shorts_editor.yml)
- Run ID: 32454151249（実行時間: 2分40秒 / Success）
- 試作テーマ：「医療と介護を一体で支える理由」（15秒 / 1080x1920）
- 生成成果物：GitHub Artifacts（shorts-prototype-output.zip）に `shorts_final.mp4` およびシーン別プレビュー画像を保存完了。

## 重要な判断・制約・セキュリティ上の注意
- 既存の正常動作しているパイプライン（Pexels取得、9:16変換、YouTubeアップロード、予約投稿、本番cron自動化）は一切変更・破壊せず維持されています。
- 今回の試作動画生成テストではYouTubeへの自動アップロードは行わず、動画生成とデザイン確認のみを安全に実施しています。
- 機密情報（token.json、client_secret_*.json）および生成動画ファイル（test_output/、*.mp4）がGit管理下に入らないよう、.gitignore で厳重に除外しています。これらのファイルは絶対にGitHubにpushしないでください。
- APIキー、Client Secret、Refresh Tokenなどの具体的な秘密情報の値は、本ファイルを含むいかなるソースコードやドキュメントにも直接記録しないでください。

## 次に必要な作業（ユーザー確認待ち）
1. 生成された試作動画のデザイン（文字サイズ、フォント、字幕位置、角丸ボックスの半透明度、背景動画との見やすさ、字幕切り替え速度、BGM音量、最後のプロフィール誘導）の確認・フィードバック。
2. 承認後、複数テーマ（7施設紹介、理念、ISR、レッドコード、通所/外来リハビリ等）のシナリオ定義と本番ワークフローへの統合。
