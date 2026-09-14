"""
YouTube Auto Short TTS 発音・字幕分離・プロソディ総合テストスイート
(Comprehensive TTS Pronunciation & Subtitle Alignment Test Suite)

【テスト項目】
Test 1: 「何科に行けばいいか」の誤読防止・字幕維持検証
Test 2: 「なんか変ですね」の非干渉検証
Test 3: 文脈に応じた読み分け検証（医療・診療科の何科 vs 通常表現）
Test 4: themes.py 全24テーマ・全72バリエーションに登場する医療・介護用語の整合性検証
Test 5: 字幕テキストと音声タイムラインの完全一致・同期検証
"""

import os
import sys
import unittest
import asyncio

# プロジェクトルートのパス追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pronunciation_dict import (
    get_spoken_text,
    apply_pronunciation_dict,
    format_spoken_prosody,
    get_pronunciation_manager
)
from voice_generator import generate_voice_with_timeline, SpeechSegment, _split_into_display_sentences
from generate_shorts_pipeline import build_dynamic_scenes_from_timeline
from themes import THEMES


class TestPronunciationSeparation(unittest.TestCase):
    """字幕テキストとTTSテキストの分離・誤読防止テスト"""

    def setUp(self):
        self.manager = get_pronunciation_manager()

    def test_01_nanika_reading_and_subtitle_separation(self):
        """
        Test 1: 「何科に行けばいいか」
        - subtitle_text は漢字の「何科に行けばいいか」を100%維持
        - spoken_text（TTS用）は「なに科に行けばいいか」または「なにか...」となり「なんか」にならない
        """
        original = "何科に行けばいいか迷っていませんか？"
        spoken = get_spoken_text(original)

        # 1. 字幕原稿（original）が変化していないことの検証
        self.assertEqual(original, "何科に行けばいいか迷っていませんか？")

        # 2. TTS用テキスト（spoken）において「何科」が「なに科」へ変換されていること
        self.assertIn("なに科", spoken)
        self.assertNotIn("何科", spoken)

        # 3. 「なんか」に誤変換されていないこと
        self.assertNotIn("なんかに行けば", spoken)

    def test_02_nanka_non_interference(self):
        """
        Test 2: 「なんか変ですね」
        - 「なんか」が「何科」のルールによって誤置換されないこと
        """
        original = "なんか変ですね。"
        spoken = get_spoken_text(original)

        # 「なんか」がそのまま維持されていること
        self.assertEqual(spoken, "なんか変ですね。")
        self.assertNotIn("なに科", spoken)

    def test_03_context_dependent_readings(self):
        """
        Test 3: 文脈依存語の識別検証
        - 医療文脈（受診・相談）の「何科」は「なに科」へ変換
        - 文脈外の一般的な語句への誤爆がないこと
        """
        # 医療文脈ケース
        medical_cases = [
            ("何科に行けばいいか迷っていませんか？", "なに科に行けばいいか迷っていませんか？"),
            ("何科に行くか迷ったらまず当院へ", "なに科に行くか迷ったらまず当院へ"),
            ("何科を受診すればよいか相談したい", "なに科を受診すればよいか相談したい"),
        ]
        for src, expected in medical_cases:
            res = apply_pronunciation_dict(src)
            self.assertEqual(res, expected, f"Failed for medical context: {src}")

        # CTA呼びかけ「方へ」（ほうへ -> かたへ の誤読防止）
        cta_cases = [
            ("姿勢を整えたい方へ。", "姿勢を整えたいかたへ。"),
            ("歩き続けたい方へ。", "歩き続けたいかたへ。"),
            ("足腰の衰えが不安な方へ。", "足腰の衰えが不安なかたへ。"),
            ("運動が続かないとお悩みの方へ。", "運動が続かないとお悩みのかたへ。")
        ]
        for src, expected in cta_cases:
            res = apply_pronunciation_dict(src)
            self.assertEqual(res, expected, f"Failed for CTA context: {src}")

    def test_04_themes_medical_terms_integrity(self):
        """
        Test 4: themes.py の全24テーマから抽出された専門用語の整合性
        全72バリエーションのナレーション原稿を一括スキャンし、
        エラーや不正な空文字列が発生しないことを検証。
        """
        total_variations = 0
        cta_sample = "西田医院の取り組みはプロフィールから。"

        for t in THEMES:
            theme_id = t.get("theme_id")
            for idx, v in enumerate(t.get("variations", [])):
                total_variations += 1
                template = v.get("narration_template", "")
                narration = template.format(cta=cta_sample)

                # 変換実行
                spoken = get_spoken_text(narration)

                # 基本アサーション
                self.assertTrue(len(spoken) > 0, f"Spoken text is empty for {theme_id} v{idx+1}")
                self.assertTrue(len(narration) > 0, f"Narration is empty for {theme_id} v{idx+1}")

                # 句点数の維持確認（文分割数が壊れていないこと）
                orig_sentences = _split_into_display_sentences(narration)
                spoken_sentences = _split_into_display_sentences(spoken)
                self.assertEqual(
                    len(orig_sentences), len(spoken_sentences),
                    f"Sentence count mismatch in {theme_id} v{idx+1}: {len(orig_sentences)} vs {len(spoken_sentences)}"
                )

        self.assertEqual(total_variations, 72, "Total theme variations should be 72")

    def test_05_speech_segment_structure(self):
        """
        Test 5: SpeechSegment 内部データ構造の整合性
        - subtitle_text と speech_text が正しく格納され、後方互換キーも充足していること
        """
        seg = SpeechSegment(
            segment_id=1,
            subtitle_text="何科に行けばいいか迷っていませんか？",
            speech_text="なに科に行けばいいか迷っていませんか？",
            start=0.0,
            end=3.5,
            duration=3.5
        )
        d = seg.to_dict()
        self.assertEqual(d["subtitle_text"], "何科に行けばいいか迷っていませんか？")
        self.assertEqual(d["speech_text"], "なに科に行けばいいか迷っていませんか？")
        self.assertEqual(d["text"], "何科に行けばいいか迷っていませんか？")
        self.assertEqual(d["spoken_text"], "なに科に行けばいいか迷っていませんか？")
        self.assertEqual(d["display_text"], "何科に行けばいいか迷っていませんか？")
        self.assertEqual(d["start"], 0.0)
        self.assertEqual(d["end"], 3.5)

    def test_06_omodarusa_reading_and_subtitle_separation(self):
        """
        Test 6: 「重だるさ」「重だるい」の誤読防止・字幕維持検証
        - subtitle_text は漢字の「重だるさ」「重だるい」を100%維持
        - spoken_text（TTS用）は「おもだるさ」「おもだるい」となり「じゅうだるさ」にならない
        """
        original = "揉んでもすぐに戻る重だるさ。"
        spoken = get_spoken_text(original)

        # 1. 字幕原稿（original）が変化していないことの検証
        self.assertEqual(original, "揉んでもすぐに戻る重だるさ。")

        # 2. TTS用テキスト（spoken）において「重だるさ」が「おもだるさ」へ変換されていること
        self.assertIn("おもだるさ", spoken)
        self.assertNotIn("重だるさ", spoken)

        # 3. 「じゅうだるさ」に誤読されていないこと
        self.assertNotIn("じゅうだるさ", spoken)

        # 4. 「重だるい」の検証
        sample_i = "重だるい感じが抜けません。"
        spoken_i = get_spoken_text(sample_i)
        self.assertIn("おもだるい", spoken_i)
        self.assertNotIn("重だるい", spoken_i)
        self.assertNotIn("じゅうだるい", spoken_i)

    def test_07_prohibited_misreadings_blacklist(self):
        """
        Test 7: 禁止誤読ブラックリストの検出排除
        - 「じゅうだるさ」「じゅうだるい」「なんかに行けば」等の禁止表現が
          いかなる入力からも生成されないことを検証
        """
        prohibited_cases = [
            ("揉んでもすぐに戻る重だるさ。", "じゅうだるさ"),
            ("重だるい筋肉の違和感。", "じゅうだるい"),
            ("何科に行けばいいか迷っていませんか？", "なんかに行けば")
        ]
        for src, forbidden in prohibited_cases:
            spoken = get_spoken_text(src)
            self.assertNotIn(forbidden, spoken, f"Prohibited misreading '{forbidden}' found in spoken text for '{src}'")

    def test_08_all_72_scenarios_comprehensive_audit(self):
        """
        Test 8: 全72シナリオに対する重要語・禁止誤読網羅検査
        - 全72シナリオのナレーション原稿を走査
        - 禁止誤読（じゅうだるさ、じゅうだるい、なんかに行けば）が全シナリオでゼロ件であること
        - 「重だるさ」を含むシナリオで「おもだるさ」へ正しく変換されていること
        - 「何科」を含むシナリオで「なに科」へ正しく変換されていること
        - 「体重」などの正規の音読み漢字が誤置換（例: おも）されていないこと
        """
        cta_sample = "西田医院の取り組みはプロフィールから。"
        forbidden_patterns = ["じゅうだるさ", "じゅうだるい", "なんかに行けば"]
        tested_scenarios = 0

        for t in THEMES:
            theme_id = t.get("theme_id")
            for idx, v in enumerate(t.get("variations", [])):
                tested_scenarios += 1
                template = v.get("narration_template", "")
                narration = template.format(cta=cta_sample)
                spoken = get_spoken_text(narration)

                # 1. 禁止誤読ワードの不在アサーション
                for fp in forbidden_patterns:
                    self.assertNotIn(
                        fp, spoken,
                        f"Prohibited pattern '{fp}' found in {theme_id} variation {idx+1}: {spoken}"
                    )

                # 2. 「重だるさ」個別チェック（theme_5_2 等）
                if "重だるさ" in narration:
                    self.assertIn(
                        "おもだるさ", spoken,
                        f"'重だるさ' was not converted to 'おもだるさ' in {theme_id} v{idx+1}"
                    )
                    self.assertNotIn(
                        "重だるさ", spoken,
                        f"Raw kanji '重だるさ' remained in spoken text in {theme_id} v{idx+1}"
                    )

                # 3. 「何科」個別チェック（theme_8_1 等）
                if "何科" in narration and ("行けば" in narration or "行く" in narration or "受診" in narration):
                    self.assertIn(
                        "なに科", spoken,
                        f"'何科' was not converted to 'なに科' in {theme_id} v{idx+1}"
                    )

                # 4. 「体重」等の通常音読みが誤変換されていないことの検証
                if "体重" in narration:
                    self.assertIn(
                        "体重", spoken,
                        f"'体重' was corrupted in {theme_id} v{idx+1}: {spoken}"
                    )

        self.assertEqual(tested_scenarios, 72, "Must audit exactly 72 scenarios")

    def test_09_audio_sentence_boundary_sync_integrity(self):
        """
        Test 9: 実音声 SentenceBoundary による字幕同期タイムライン整合性検証
        - Edge TTS を実際に呼び出し、SpeechSegment および dynamic_scenes が
          字幕表示（漢字）を完全維持しつつ、実音声タイムラインと整合することを検証
        """
        target_text = "揉んでもすぐに戻る重だるさ。組織同士が滑り合うよう丁寧な手技で動きの根本を整えます。"
        out_audio = os.path.join("test_output", "test_omodarusa_sync.mp3")

        ok, timeline = generate_voice_with_timeline(
            text=target_text,
            output_path=out_audio,
            voice_config={"voice": "ja-JP-NanamiNeural", "rate": "+0%", "pitch": "+0Hz"}
        )

        self.assertTrue(ok, "TTS generation must succeed")
        self.assertTrue(len(timeline) >= 2, f"Should have at least 2 segments, got {len(timeline)}")

        # Segment 1 の検証
        seg1 = timeline[0]
        # 字幕テキストは漢字「重だるさ」を100%保持
        self.assertIn("重だるさ", seg1["subtitle_text"])
        self.assertIn("重だるさ", seg1["text"])
        # 音声テキストは「おもだるさ」に補正されていること
        self.assertIn("おもだるさ", seg1["speech_text"])
        self.assertIn("おもだるさ", seg1["spoken_text"])
        self.assertNotIn("じゅうだるさ", seg1["speech_text"])

        # タイムラインの整合性
        self.assertTrue(seg1["start"] >= 0.0)
        self.assertTrue(seg1["end"] > seg1["start"])
        self.assertTrue(seg1["duration"] > 0.0)

        # dynamic_scenes 構築の検証（最初のシーンは0.0s固定）
        scenes = build_dynamic_scenes_from_timeline(timeline, total_video_duration=15.0)
        self.assertEqual(len(scenes), len(timeline))
        self.assertEqual(scenes[0]["start"], 0.0)
        self.assertIn("重だるさ", scenes[0]["raw_text"])


if __name__ == '__main__':
    unittest.main(verbosity=2)
