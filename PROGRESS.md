# YouTube自動予約投稿プロジェクト 進捗管理 (PROGRESS.md)

## 現在の進捗状況
- M1（完了）：代表テーマ（テーマ1-1：痛みの先にある生活）によるNanamiNeural（話速-5%）ナレーション付きShorts動画生成・フォールバック・タイミング・音量バランス・15秒収まりの検証完了。
- M2（完了）：確定済み21テーマ（全7カテゴリー×各3テーマ）のシナリオ定義データ組み込み（themes.py）。
- M3（完了）：21テーマの順番制自動ローテーション関数（get_next_theme）の実装および全8項目の単体テスト合格（ローカルコミット完了、未push）。
- M4（完了）：本番自動投稿ワークフロー接続前の事前調査・設計確認（コード変更なし・方針確定）。
- M5（実装・テスト完了 / 承認待ち）：本番自動投稿ワークフロー接続、状態確定の投稿後分離（select_next_theme / commit_theme_state）、同時実行防止（concurrency）、投稿成功時のみのGit Auto-Commit/Push機構の実装とローカル検証完了。

## 直近の作業内容（M5）
1. themes.py：
   - select_next_theme()（読み込み専用）と commit_theme_state()（投稿後確定専用）の追加。
   - 既存の get_next_theme() は後方互換性を100%維持。
2. generate_shorts_pipeline.py：
   - select_next_theme() によるテーマ取得と、後続ステップ用の一時メタデータ（test_output/current_theme.json）出力の追加。
3. .github/workflows/production_auto_post.yml：
   - concurrency（二重実行防止）および permissions: contents: write の設定。
   - 日本語フォント（fonts-noto-cjk）のインストールステップ追加。
   - ナレーション＋字幕＋BGM合成ステップ（generate_shorts_pipeline.py）の追加。
   - YouTube予約投稿（youtube_upload.py）への動的タイトル・説明文連携。
   - 投稿成功時（if: success()）のみの state/theme_state.json 確定コミット＆プッシュステップ追加。
4. テスト検証：
   - ローカルでの状態非変更確認、失敗時非進行確認、成功時確定保存確認、ローテーション順序確認、THEME_ID指定確認、YAML構文チェックの全項目合格。

## 未実施事項（ユーザー承認待ち）
- Git commit / Git push
- GitHub Actions 本番ワークフローのトリガー実行
- YouTube への本番予約アップロード
