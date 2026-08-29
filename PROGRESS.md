# YouTube自動予約投稿プロジェクト 進捗管理 (PROGRESS.md)

## 最終目標
GitHub Actions から毎日定期実行（cron）にて、Pexels素材取得 → テーマ決定・ローテーション → TTSナレーション（NanamiNeural）→ 字幕（BudouX）→ BGM（4和音アルペジオ）→ 9:16 Shorts動画生成 → YouTube Data API v3 認証（OAuth 2.0 In-Production Refresh Token）→ 動画アップロード → publishAtによる24時間後予約公開 → state/theme_state.json の確定コミット＆プッシュ を完全無人で継続実行するシステムの完成。

## 現在の進捗状況
- STEP 1（完了）：プロジェクト実体・Git履歴・全コード・ワークフロー・Secrets・Google Cloud設定の徹底調査完了。
- STEP 2（完了）：Google Cloud / YouTube API基盤の仕様整理および最小構成の確定（YouTube Data API v3 有効、Scope: `https://www.googleapis.com/auth/youtube.upload`、Publishing Status: In Production、個人所有チャンネル自動化用途におけるVerification審査不要の確定）。
- STEP 3（完了）：OAuth Client（Desktop App type, client_secret_new.json / Client ID: 1012793477083-soc1vr...）の認証経路確立。
- STEP 4（完了）：新OAuth Clientに基づく有効なRefresh Token（token_verified.json）の取得および整合性確認。
- STEP 5（完了）：ローカル環境でのYouTube APIアクセストークン自動リフレッシュおよびAPI接続の実証テスト成功。
- STEP 6（完了）：GitHub Secrets（YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN, PEXELS_API_KEY）の更新・同期確認。
- STEP 7（完了）：GitHub Actions上でのOAuth認証単独テスト（test_youtube_auth.yml / Run ID: 33252148780）実行・SUCCESS確認。
- STEP 8（完了）：YouTube Data API v3 による実動画アップロードおよび `publishAt` による予約公開（privacyStatus: private）の実証完了（動画ID: EeduEACKWvc）。
- STEP 9（完了）：動画生成パイプライン（21テーマ、NanamiNeural TTS、BudouX自然改行字幕、BGMミキシング、1080x1920 9:16 15秒動画）のローカル完全レンダリング検証完了。
- STEP 10（完了）：`youtube_upload.py`（publishAt指定時のprivacyStatus: private自動保証）および本番定期実行ワークフロー（`.github/workflows/production_auto_post.yml`）の予約公開パイプラインへの更新完了。

## 認証・運用仕様の確定事実（推測を排除した実証結果）
1. **Publishing Status**: In Production
   - TestingモードではRefresh Tokenが7日間で失効する仕様のため、長期毎日の無人自動投稿には In Production が必須。
2. **OAuth Scope**: `https://www.googleapis.com/auth/youtube.upload`
   - アップロード専用の最小スコープ。不要な権限を含めない最小構成。
3. **Verification（審査）とBranding**:
   - 一般第三者へのアプリ公開・配布ではなく、開発者自身が所有するYouTubeチャンネルへの自動投稿であるため、Googleによる審査（Verification）およびBranding承認は不要。Unverified（未審査）状態のままでRefresh Tokenは無期限で自動更新され正常動作する。
4. **予約公開（publishAt）仕様**:
   - YouTube Data API v3 仕様により、`publishAt` を指定してアップロードする場合は `privacyStatus` を必ず `private` に設定する必要がある。YouTube側で指定日時に自動的に公開（public）に切り替わる。

## 主要ファイル構成
- `.github/workflows/production_auto_post.yml`: 毎日JST 09:00定期実行＆手動実行対応の統合予約投稿ワークフロー
- `.github/workflows/test_youtube_auth.yml`: GitHub Actions上でのOAuth認証確認用ワークフロー
- `youtube_upload.py`: YouTube Data API v3 アップロード＆予約公開スクリプト（publishAt自動private安全処理付き）
- `generate_shorts_pipeline.py`: TTS・字幕・BGM・9:16動画生成パイプライン
- `themes.py`: 21テーマ（7カテゴリー×3テーマ）シナリオ定義＆自動ローテーション管理
- `state/theme_state.json`: 現在のテーマ進行状態管理ファイル
