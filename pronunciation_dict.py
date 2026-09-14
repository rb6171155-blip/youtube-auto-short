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
            {"id": "katahe_fb", "surface": "方へ", "match_pattern": "(?<=[たいるい]|お悩み|不安な)方へ", "replacement": "かたへ", "priority": 90},
            {"id": "omodarusa_fb", "surface": "重だるさ", "match_pattern": "重だるさ", "replacement": "おもだるさ", "priority": 90},
            {"id": "omodarui_fb", "surface": "重だるい", "match_pattern": "重だるい", "replacement": "おもだるい", "priority": 90}
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
        台本テキストから以下を多層的に抽出し、
        辞書未登録かつ日常語ホワイトリスト外の専門用語・誤読リスク候補語を検出する。
        1. 連続漢字熟語（2文字以上: 例 理学療法士、運動療法）
        2. 漢字＋ひらがな複合語・接尾辞名詞/形容詞（例: 重だるさ、重だるい、動かしにくさ、引っかかり）
        3. 大文字英字略語（例: ISR, PT, OT）
        4. 長大カタカナ専門用語候補（4文字以上: 例: レッドコード、ハイドロリリース）
        一般的な動詞・形容詞の日常的活用語（揉んで、戻る、整えます等）は過剰検知しない。
        """
        common_whitelist = {
            # 医療・施設・スタッフ
            "西田", "医院", "治療", "医療", "介護", "当院", "病院", "クリニック", "医師", "看護",
            "看護師", "専門職", "スタッフ", "ケアマネジャー", "理学療法士", "専門医", "受診", "診察",
            "入院", "退院", "通院", "在宅", "訪問", "通い", "泊まり", "施設", "外来", "大学病院",
            "地域病院", "ホームドクター", "相談窓口", "連携", "地域密着", "運営母体", "運営", "母体",
            "専門医療", "専門外来", "連携体制", "医療機関", "専門的", "専門手技", "専門",
            # 身体・症状・部位
            "身体", "体全体", "全身", "体幹", "深層", "深層部", "深層筋肉", "筋肉", "インナーマッスル",
            "関節", "関節周囲", "骨盤", "足首", "肩甲骨", "足腰", "膝以外", "膝ばかり", "血管",
            "心臓", "腹部", "血液", "血圧", "血糖値", "症状", "苦痛", "違和感", "状態", "体調",
            "体調不良", "体力", "体力回復", "衰え", "疲労", "疲労感", "安心感", "負担感", "心地よさ",
            "感覚", "左右差", "姿勢", "連動性", "連動", "可動域", "滑走性", "柔軟", "癒着",
            "組織", "組織間", "組織同士", "組織本来", "心地", "気持",
            # 動作・リハビリ・運動
            "動き", "動かしやすさ", "動きやすさ", "動きにくさ", "動かしにくさ", "歩行", "立位", "座位",
            "立ち上がり", "階段", "上り", "下り", "段差", "移動", "転倒", "運動", "運動療法",
            "運動習慣", "体操", "スクワット", "ストレッチ", "リハビリ", "機能訓練", "自主トレ",
            "手技", "手技療法", "スリング", "レッドコード", "マッサージ", "練習", "習慣", "指導",
            "実践", "実践的", "動作", "アプローチ", "引っかかり",
            # 日常・生活・支援
            "生活", "日常生活", "日常", "在宅生活", "在宅介護", "自宅", "居場所", "家族", "笑顔",
            "未来", "背景", "安心", "安全", "快適", "元気", "自信", "希望", "交流", "言葉",
            "仲間", "会話", "送迎", "食事", "入浴", "排泄", "自立", "支援", "応援", "見守り",
            "生活環境", "入院生活", "退院後", "退院直後", "自分", "一人", "一度", "一歩", "一日中",
            "楽しみ", "楽しさ", "丁寧", "大切", "一緒", "不安",
            # 検査・予防・制度
            "検査", "健診", "健康診断", "特定健診", "各種健診", "予防", "予防接種", "各種予防接種",
            "早期発見", "早期", "発見", "処置", "医療処置", "胃ろう", "インスリン", "湿布",
            "超音波", "心電図", "レントゲン", "尿検査", "血液検査", "基本料金", "月額定額制",
            "定額", "月額", "利用回数", "費用", "介護費用", "見通し", "見通", "制度", "サービス",
            "プログラム", "土曜日",
            # 一般語・形容・副詞・接続
            "原因", "根本", "根本的", "全体", "評価", "特定", "場所", "相談", "些細", "幅広",
            "適切", "連続", "無意識", "継続", "後回し", "後回", "自然", "刺激", "確認", "長引く",
            "長引", "天井", "自身", "可能", "日頃", "わずか", "変化", "察知", "迅速", "直後",
            "一体", "普段", "普段使い", "高度", "筋力", "想定", "前向き", "前向", "時間", "一日",
            "気分", "秘訣", "頑固", "頑丈", "本来", "両手", "体重", "負担", "最小", "最小限",
            "環境", "混乱", "基本", "料金", "利用", "回数", "最近", "仕事", "安定", "段階的",
            "一般的", "個人差", "効果的", "対応", "必要", "気軽", "健康", "健康寿命", "簡単",
            "心配", "徹底", "短時間", "個別", "集団", "担当", "連絡", "内科", "整形外科",
            "リハビリ科", "プロフィール", "サポート", "トータルサポート", "スタート", "ストレス",
            "スピード", "スムーズ", "チェック", "デイケア", "ネットワーク", "ノルウェー", "バランス",
            "ピンポイント", "大丈夫", "実際", "当日", "摩擦", "数値", "未然", "本人", "様子",
            "機会", "毎日", "無理", "病気", "着実", "突発的", "結果", "苦手", "要望", "解放",
            "診療", "途中", "通所", "限界", "顔なじみ", "余分", "常駐", "長持ち", "長持",
            "地域"
        }

        # 1. 2文字以上の連続漢字熟語
        kanji_terms = re.findall(r"[\u4e00-\u9fff]{2,}", text)
        # 2. 漢字＋ひらがな接尾辞複合語（名詞・形容詞）
        compound_terms = re.findall(r"[\u4e00-\u9fff]+[ぁ-ん]{1,3}(?:さ|み|だる[いさ]|にく[いさ]|やす[いさ]|かかり)", text)
        # 3. 大文字英字略語（2文字以上）
        abbrev_terms = re.findall(r"[A-Z]{2,}", text)
        # 4. カタカナ専門用語候補（4文字以上）
        katakana_terms = re.findall(r"[\u30a1-\u30f6ー]{4,}", text)

        candidate_terms = set(kanji_terms + compound_terms + abbrev_terms + katakana_terms)

        unknowns = []
        for term in candidate_terms:
            if term not in self.known_surfaces and term not in common_whitelist:
                unknowns.append(term)

        if unknowns:
            # 運用ログへの記録（警告ではなく案内として出力）
            print(f"[PRONUNCIATION SCAN] Notice: Unregistered candidate term(s) in script: {sorted(unknowns)}")

        return sorted(unknowns)


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
