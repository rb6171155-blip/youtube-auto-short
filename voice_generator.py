import os
import sys
import re
import asyncio
from typing import List, Dict, Any, Tuple
import edge_tts
from pronunciation_dict import get_spoken_text, get_pronunciation_manager

OUTPUT_DIR = "test_output"
DEFAULT_VOICE = "ja-JP-NanamiNeural"
DEFAULT_RATE = "+0%"
DEFAULT_PITCH = "+0Hz"


class SpeechSegment:
    """
    音声と字幕の同期タイムラインを保持する内部データ構造
    - subtitle_text: 画面字幕表示用正式テキスト（漢字・正式表記）
    - speech_text: TTS読み上げ用テキスト（なに科 等の発音補正済み表記）
    - start / end / duration: 実音声タイムスタンプ（秒）
    """
    def __init__(self, segment_id: int, subtitle_text: str, speech_text: str,
                 start: float = 0.0, end: float = 0.0, duration: float = 0.0):
        self.segment_id = segment_id
        self.subtitle_text = subtitle_text
        self.speech_text = speech_text
        self.start = round(start, 2)
        self.end = round(end, 2)
        self.duration = round(duration, 2)
        self.lines: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "segment_id": self.segment_id,
            "subtitle_text": self.subtitle_text,
            "speech_text": self.speech_text,
            "text": self.subtitle_text,       # pipeline / editor 後方互換キー（字幕用漢字テキスト）
            "spoken_text": self.speech_text, # pipeline / editor 後方互換キー（音声用テキスト）
            "display_text": self.subtitle_text,
            "start": self.start,
            "end": self.end,
            "duration": self.duration,
            "lines": self.lines
        }


async def _generate_edge_tts_with_timeline(text: str, output_path: str, voice: str = DEFAULT_VOICE,
                                          rate: str = DEFAULT_RATE, pitch: str = DEFAULT_PITCH) -> List[Dict[str, Any]]:
    """
    edge-tts を非同期実行し、音声MP3を保存すると同時に
    SentenceBoundary メタデータから文単位の実音声タイムスタンプを取得する
    """
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    audio_data = bytearray()
    raw_sentences = []

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data.extend(chunk["data"])
        elif chunk["type"] == "SentenceBoundary":
            # 100ナノ秒単位を秒（float）に変換
            start_sec = chunk["offset"] / 10_000_000.0
            dur_sec = chunk["duration"] / 10_000_000.0
            end_sec = start_sec + dur_sec
            sentence_text = chunk["text"]
            raw_sentences.append({
                "spoken_text": sentence_text,
                "start": round(start_sec, 2),
                "end": round(end_sec, 2),
                "duration": round(dur_sec, 2)
            })

    if not audio_data:
        raise ValueError("No audio data received from edge-tts")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(audio_data)

    return raw_sentences


def _split_into_display_sentences(text: str) -> List[str]:
    """
    ナレーション原文を句読点（。！？!?）単位で分割し、句読点を保持した文リストを返す
    """
    raw_sentences = [s.strip() for s in re.split(r'([。！？!?])', text) if s.strip()]
    merged = []
    for s in raw_sentences:
        if s in ['。', '！', '？', '!', '?'] and merged:
            merged[-1] += s
        else:
            merged.append(s)
    return merged if merged else [text]


def _align_sentences_with_subtitles(raw_sentences: List[Dict[str, Any]], display_sentences: List[str]) -> List[SpeechSegment]:
    """
    TTSの SentenceBoundary と画面字幕用テキスト（display_sentences）を整合させ、
    文単位の SpeechSegment リストを構築する。
    文数の不一致が生じた場合でも安全にマッピングし、字幕テキストの欠落やズレを防ぐ。
    """
    num_audio = len(raw_sentences)
    num_disp = len(display_sentences)

    segments = []

    if num_audio == 0:
        # 音声文情報が空の場合のフォールバック
        for idx, dt in enumerate(display_sentences):
            segments.append(SpeechSegment(
                segment_id=idx + 1,
                subtitle_text=dt,
                speech_text=dt,
                start=0.0,
                end=0.0,
                duration=0.0
            ))
        return segments

    if num_audio == num_disp:
        # 完全一致ケース（理想ケース）
        for i in range(num_audio):
            s = raw_sentences[i]
            dt = display_sentences[i]
            segments.append(SpeechSegment(
                segment_id=i + 1,
                subtitle_text=dt,
                speech_text=s["spoken_text"],
                start=s["start"],
                end=s["end"],
                duration=s["duration"]
            ))
    elif num_audio > num_disp:
        # 音声側の境界分割が字幕より多い場合（文中の読点等で分割されたケース）
        # 字幕文のインデックスに可能な限り割り当て、あふれた分は最後の字幕文にマージ
        for i in range(num_audio):
            s = raw_sentences[i]
            disp_idx = min(i, num_disp - 1)
            dt = display_sentences[disp_idx]
            segments.append(SpeechSegment(
                segment_id=i + 1,
                subtitle_text=dt,
                speech_text=s["spoken_text"],
                start=s["start"],
                end=s["end"],
                duration=s["duration"]
            ))
    else:
        # 音声側の境界分割が字幕より少ない場合
        # 字幕側の全テキストが確実に表示されるよう、残りの字幕文を音声タイムラインに対応付け
        for i in range(num_disp):
            audio_idx = min(i, num_audio - 1)
            s = raw_sentences[audio_idx]
            dt = display_sentences[i]
            segments.append(SpeechSegment(
                segment_id=i + 1,
                subtitle_text=dt,
                speech_text=s["spoken_text"],
                start=s["start"],
                end=s["end"],
                duration=s["duration"]
            ))

    return segments


def generate_voice_with_timeline(text: str, output_path: str, voice_config: dict = None,
                                display_text: str = None) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    ナレーション音声を生成し、文単位の正確な実音声タイムラインを返す。
    発音・プロソディ補正（pronunciation_dict / 外部JSON）を適用し、
    画面字幕用の漢字表記（subtitle_text）とTTS読み上げ用テキスト（speech_text）を
    SpeechSegment 内部データ構造によって完全に分離して処理する。
    """
    if voice_config is None:
        voice_config = {}

    if display_text is None:
        display_text = text

    voice = voice_config.get('voice', DEFAULT_VOICE)
    rate = voice_config.get('rate', DEFAULT_RATE)
    pitch = voice_config.get('pitch', DEFAULT_PITCH)

    # 発音補正＋プロソディ（ブレス）補正の適用（字幕原文は維持し、TTS用テキストのみ補正）
    spoken_text = get_spoken_text(text)

    print(f"[TTS] Generating narration with timeline from edge-tts...")
    print(f"[TTS] Voice: {voice}, Rate: {rate}, Pitch: {pitch}")
    print(f"[TTS] Subtitle Text (字幕・正式漢字): \"{display_text}\"")
    print(f"[TTS] Spoken Text   (音声・TTS最適化): \"{spoken_text}\"")

    try:
        raw_sentences = asyncio.run(_generate_edge_tts_with_timeline(spoken_text, output_path, voice, rate, pitch))

        # 字幕表示用テキスト（原文の漢字表記）を各文のタイムラインにマッピング
        display_sentences = _split_into_display_sentences(display_text)
        speech_segments = _align_sentences_with_subtitles(raw_sentences, display_sentences)

        # 後方互換性のため辞書リスト形式で返却
        sentences_dict_list = [seg.to_dict() for seg in speech_segments]

        file_size = os.path.getsize(output_path)
        print(f"[TTS SUCCESS] Generated: {output_path} ({file_size} bytes, {len(speech_segments)} segments)")
        for idx, seg in enumerate(speech_segments):
            print(f"  Segment {idx + 1}: Subtitle=\"{seg.subtitle_text}\" Spoken=\"{seg.speech_text}\" Time={seg.start}s->{seg.end}s")

        return True, sentences_dict_list
    except Exception as e:
        print(f"[TTS ERROR] Failed to generate TTS with timeline: {e}", file=sys.stderr)
        return False, []


def generate_voice(text: str, output_path: str, provider: str = "edge", voice_config: dict = None) -> bool:
    """既存の後方互換用ラッパー関数"""
    success, _ = generate_voice_with_timeline(text, output_path, voice_config)
    return success


if __name__ == '__main__':
    sample_text = "何科に行けばいいか迷っていませんか？特定の専門に絞らないからこそ、身体のお悩みを何でも相談できる場所があります。西田医院の取り組みはプロフィールから。"
    test_out = os.path.join(OUTPUT_DIR, "tts_voice_generator_test.mp3")
    ok, timeline = generate_voice_with_timeline(sample_text, test_out)
    print(f"\nTest execution ok: {ok}")
    for sc in timeline:
        print(f"[{sc['start']}s - {sc['end']}s] Subtitle: {sc['text']} | Spoken: {sc['spoken_text']}")
