"""
日本語TTS発音補正・プロソディ制御および文脈辞書マネージャー (Pronunciation & Prosody Module)

【設計原則】
1. 字幕表示用テキスト（subtitle_text / 原文の自然な漢字表記）とTTS音声読み上げ用テキスト（speech_text）を完全分離する。
2. 個別の text.replace() によるモグラ叩きを禁止し、config/pronunciation_dictionary.json にて一元管理する。
3. 4層アーキテクチャ（Layer 1: 表記, Layer 2: 読み, Layer 3: アクセントメタデータ, Layer 4: TTSエンジン変換）を確立。
4. 文脈パターン（context_pattern / match_pattern）に基づく文脈依存語の適切な発音誘導（例: 「何科」の診療科イントネーション誘導）。
5. 将来の専門用語追加にもPythonコードの変更なしでJSON辞書から安全に反映可能とする。
6. 未知語候補を検出した場合はログに出力し、AIによる無断書き換えは行わない。
"""

import os
import sys
import json
import re
from typing import List, Dict, Any, Optional

DEFAULT_DICT_PATH = os.path.join(os.path.dirname(__file__), "config", "pronunciation_dictionary.json")

class PronunciationEntry:
    """
    4層アーキテクチャに基づく発音辞書エントリ
    - Layer 1: surface (表記)
    - Layer 2: reading (読み)
    - Layer 3: accent_type (アクセント・プロソディメタデータ)
    - Layer 4: speech_text (TTS向け最適化テキスト)
    """
    def __init__(self, data: Dict[str, Any]):
        self.id: str = data.get("id", "")
        self.surface: str = data.get("surface", "")
        self.reading: str = data.get("reading", "")
        self.speech_text: str = data.get("speech_text", self.surface)
        self.accent_type: str = data.get("accent_type", "heiban")
        self.context: str = data.get("context", "")
        self.match_pattern: str = data.get("match_pattern", re.escape(self.surface))
        self.replacement: str = data.get("replacement", self.speech_text)
        self.priority: int = data.get("priority", 50)
        self.notes: str = data.get("notes", "")

    def __repr__(self):
        return f"<PronunciationEntry id={self.id} surface={self.surface} reading={self.reading}>"


class PronunciationManager:
    """
    外部JSON発音辞書を統括し、発音補正・プロソディ補正・未知語検出を実行するマネージャー
    """
    def __init__(self, dict_path: str = DEFAULT_DICT_PATH):
        self.dict_path = dict_path
        self.entries: List[PronunciationEntry] = []
        self.prosody_rules: List[Dict[str, str]] = []
        self.known_surfaces: set = set()
        self.load_dictionary()

    def load_dictionary(self):
        """
        外部発音辞書JSONをロード。存在しない場合や破損時は安全なデフォルトフォールバックを適用。
        """
        if not os.path.exists(self.dict_path):
            print(f"[PRONUNCIATION WARNING] Dictionary file not found at {self.dict_path}. Using fallback rules.", file=sys.stderr)
            self._load_fallback_rules()
            return

        try:
            with open(self.dict_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            raw_entries = data.get("entries", [])
            self.entries = [PronunciationEntry(e) for e in raw_entries]
            # 優先度（priority）降順、パターン文字列長降順でソート（より具体的・長文脈のルールを優先）
            self.entries.sort(key=lambda x: (x.priority, len(x.match_pattern)), reverse=True)
            self.prosody_rules = data.get("prosody_rules", [])
            self.known_surfaces = {e.surface for e in self.entries if e.surface}
            
            print(f"[PRONUNCIATION] Successfully loaded {len(self.entries)} entries and {len(self.prosody_rules)} prosody rules from {os.path.basename(self.dict_path)}")
        except Exception as e:
            print(f"[PRONUNCIATION ERROR] Failed to parse dictionary {self.dict_path}: {e}", file=sys.stderr)
            self._load_fallback_rules()

    def _load_fallback_rules(self):
        """緊急時の最小限のハードコードフォールバック"""
        fallback_data = [
            {"id": "nanika_fb", "surface": "何科", "match_pattern": "何科(?=に(?:行けば|行く|受診|かかる|相談|迷っ))", "replacement": "なに科", "priority": 100},
            {"id": "katahe_fb", "surface": "方へ", "match_pattern": "(?<=[たいるい]|お悩み|不安な)方へ", "replacement": "かたへ", "priority": 90}
        ]
        self.entries = [PronunciationEntry(e) for e in fallback_data]
        self.prosody_rules = [
            {"pattern": "(西田医院では)(?!、)", "replacement": "\\1、"},
            {"pattern": "(詳しくは|取り組みは|詳細は)(?!、)", "replacement": "\\1、"}
        ]
        self.known_surfaces = {e.surface for e in self.entries}

    def apply_pronunciation(self, text: str) -> str:
        """
        ナレーション原文に対して発音補正ルールを適用し、誤読を防止したTTS読み上げ用文字列を生成する。
        （字幕表示用テキストには影響を与えない）
        """
        if not text:
            return ""

        corrected = text
        for entry in self.entries:
            try:
                pattern = entry.match_pattern
                replacement = entry.replacement
                if pattern and re.search(pattern, corrected):
                    corrected = re.sub(pattern, replacement, corrected)
            except re.error as err:
                print(f"[PRONUNCIATION ERROR] Invalid regex pattern in entry {entry.id}: {err}", file=sys.stderr)

        return corrected

    def format_prosody(self, text: str) -> str:
        """
        TTS読み上げ用テキストに対して、人間らしい自然な文節・ブレス（息継ぎ）を与える読点を配置する。
        重複読点や句点直前の不正読点を自動整形し、文分割（句点数）を破壊しない。
        """
        if not text:
            return ""

        result = text
        for rule in self.prosody_rules:
            try:
                pattern = rule.get("pattern", "")
                replacement = rule.get("replacement", "")
                if pattern and replacement:
                    result = re.sub(pattern, replacement, result)
            except re.error as err:
                print(f"[PROSODY ERROR] Invalid regex in prosody rule: {err}", file=sys.stderr)

        # 連続読点（例: 、、）を単一読点へ正規化
        result = re.sub(r"、+", "、", result)

        # 句点・感嘆符・疑問符直前の不要な読点を除去（例: 、。 -> 。）
        result = re.sub(r"、([。！？!?])", r"\1", result)

        return result

    def get_spoken_text(self, text: str) -> str:
        """
        ナレーション原稿（字幕用マスター）から、
        1. 未知語候補スキャン（ログ記録）
        2. 発音補正（単語・文脈単位の誤読防止）
        3. プロソディ・ブレス補正（自然な息継ぎ・読点制御）
        を順次適用し、edge-tts 読み上げ専用の Spoken Text を生成する。
        """
        if not text:
            return ""

        # 未知語検出（ログ通知）
        self.detect_unknown_terms(text)

        # ステップ1: 発音補正
        pron_corrected = self.apply_pronunciation(text)

        # ステップ2: プロソディ・ブレス補正
        spoken_text = self.format_prosody(pron_corrected)

        return spoken_text

    def detect_unknown_terms(self, text: str) -> List[str]:
        """
        台本テキストから2文字以上の漢字語句を抽出し、
        辞書未登録の専門用語候補が存在する場合にログ通知を行う。
        """
        common_whitelist = {
            "西田", "医院", "治療", "生活", "笑顔", "未来", "背景", "医療", "介護", "身体", "原因",
            "全体", "評価", "骨盤", "足首", "根本", "動き", "湿布", "関節", "違和感", "退院", "体力",
            "不安", "専門", "回復", "入院", "日常", "自分", "常駐", "応援", "最近", "時間", "元気",
            "一日", "気分", "体操", "秘訣", "頑固", "手技", "療法", "組織", "本来", "両手", "体重",
            "負担", "運動", "最小", "通い", "泊まり", "訪問", "施設", "環境", "混乱", "基本", "料金",
            "月額", "定額", "利用", "回数", "費用", "見通", "連携", "特定", "場所", "相談", "病院",
            "些細", "体調", "不良", "地域", "当院", "幅広", "診察", "適切", "安心", "連続", "練習",
            "無意識", "左右", "姿勢", "継続", "後回", "習慣", "指導", "自信", "心地", "感覚", "肩甲骨",
            "安全", "体幹", "深層", "自然", "刺激", "家族", "柔軟", "自宅", "希望", "検査", "心臓",
            "血管", "腹部", "症状", "苦痛", "状態", "確認", "血液", "健診", "早期", "発見", "予防",
            "接種", "長引", "足腰", "衰え", "転倒", "天井", "自身", "可能", "運営", "母体", "処置",
            "継続", "日頃", "わずか", "変化", "察知", "迅速", "受診", "直後", "医師", "看護", "一体",
            "大学", "普段", "高度", "筋力", "連動", "快適", "階段", "上り", "下り", "椅子", "立ち",
            "上がり", "段差", "移動", "実践", "想定", "前向", "居場所", "交流", "言葉"
        }

        # 2文字以上の漢字熟語を抽出
        kanji_terms = re.findall(r"[\u4e00-\u9fff]{2,}", text)
        unknowns = []
        for term in set(kanji_terms):
            if term not in self.known_surfaces and term not in common_whitelist:
                unknowns.append(term)

        if unknowns:
            # 運用ログへの記録（警告ではなく案内として出力）
            print(f"[PRONUNCIATION SCAN] Notice: Unregistered candidate term(s) in script: {unknowns}")

        return unknowns


# ==============================================================================
# グローバルシングルトンインスタンスおよび後方互換用関数
# ==============================================================================
_manager = PronunciationManager()

def get_pronunciation_manager() -> PronunciationManager:
    """PronunciationManager インスタンスを取得"""
    return _manager

def apply_pronunciation_dict(text: str) -> str:
    """後方互換ラッパー: 発音補正"""
    return _manager.apply_pronunciation(text)

def format_spoken_prosody(text: str) -> str:
    """後方互換ラッパー: プロソディ補正"""
    return _manager.format_prosody(text)

def get_spoken_text(text: str) -> str:
    """後方互換ラッパー: ナレーション原稿 -> TTS読み上げ専用テキスト"""
    return _manager.get_spoken_text(text)


if __name__ == '__main__':
    test_cases = [
        "何科に行けばいいか迷っていませんか？特定の専門に絞らないからこそ、身体のお悩みを何でも相談できる場所があります。",
        "なんか変ですね。",
        "ふらつきやすい姿勢を整えたい方へ。自分の体重を利用したレッドコードで、体の奥の筋肉を刺激します。西田医院の取り組みはプロフィールから。",
        "インスリンや胃ろうなどの医療処置が必要な方でも、住み慣れた自宅での生活を継続できます。"
    ]
    print("=== Pronunciation & Prosody Module Test ===")
    for idx, t in enumerate(test_cases):
        print(f"\n--- Test {idx + 1} ---")
        print("Master (字幕用): ", t)
        print("Pron Corrected: ", apply_pronunciation_dict(t))
        print("Spoken (TTS用):  ", get_spoken_text(t))
