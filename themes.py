"""
西田医院グループ 確定済み21テーマ シナリオ定義データ (M2/M3/M5)
NanamiNeural (話速: -5%) 向けに最適化されたナレーション原稿と字幕原稿を完全分離で管理。
"""
import os
import json

THEMES = [
    # ----------------------------------------------------
    # 【テーマ1：理念】
    # ----------------------------------------------------
    {
        "theme_id": "theme_1_1",
        "category": "理念",
        "title": "痛みの先にある生活 #Shorts",
        "narration": "痛みを和らげること。それはゴールではなく、スタートです。西田医院では、あなたが笑顔で暮らし続けられるよう、生活の背景まで一緒に考えます。",
        "scenes": [
            {
                "start": 0.0,
                "end": 11.5,
                "tag": "西田医院が大切にしていること",
                "lines": ["痛みを減らし、", "その先の生活へ。"]
            },
            {
                "start": 11.5,
                "end": 15.0,
                "tag": "公式ホームページ・施設情報",
                "lines": ["詳しくは", "プロフィールから"]
            }
        ]
    },
    {
        "theme_id": "theme_1_2",
        "category": "理念",
        "title": "医療と介護をつなぐ理由 #Shorts",
        "narration": "医療だけでは、生活を支えきれません。だから私たちは、介護とひとつにつなげています。",
        "scenes": [
            {
                "start": 0.0,
                "end": 11.5,
                "tag": "医療と介護の連携",
                "lines": ["医療と介護。", "ひとつにつなぐ理由。"]
            },
            {
                "start": 11.5,
                "end": 15.0,
                "tag": "公式ホームページ・施設情報",
                "lines": ["詳しくは", "プロフィールから"]
            }
        ]
    },
    {
        "theme_id": "theme_1_3",
        "category": "理念",
        "title": "自分の足で歩き続けるために #Shorts",
        "narration": "いくつになっても、自分の足で行きたい場所へ行けること。その願いを支えるため、日々の予防と運動をサポートしています。",
        "scenes": [
            {
                "start": 0.0,
                "end": 11.5,
                "tag": "健康寿命と予防",
                "lines": ["いつまでも、", "自分の足で歩くために。"]
            },
            {
                "start": 11.5,
                "end": 15.0,
                "tag": "公式ホームページ・施設情報",
                "lines": ["詳しくは", "プロフィールから"]
            }
        ]
    },

    # ----------------------------------------------------
    # 【テーマ2：外来リハ】
    # ----------------------------------------------------
    {
        "theme_id": "theme_2_1",
        "category": "外来リハ",
        "title": "痛む場所だけを見ないリハビリ #Shorts",
        "narration": "膝が痛いときでも、原因は別の場所にあることも。体全体のバランスを丁寧に評価します。",
        "scenes": [
            {
                "start": 0.0,
                "end": 11.5,
                "tag": "外来リハビリの視点",
                "lines": ["痛む場所だけでなく、", "体全体のバランスを見る。"]
            },
            {
                "start": 11.5,
                "end": 15.0,
                "tag": "公式ホームページ・施設情報",
                "lines": ["詳しくは", "プロフィールから"]
            }
        ]
    },
    {
        "theme_id": "theme_2_2",
        "category": "外来リハ",
        "title": "姿勢と歩き方の見直し #Shorts",
        "narration": "無意識の歩き方のクセが、関節に負担をかけていることがあります。理学療法士と一緒に、無理のない体の動かし方を練習します。",
        "scenes": [
            {
                "start": 0.0,
                "end": 11.5,
                "tag": "理学療法士のアプローチ",
                "lines": ["歩き方のクセを見直し、", "負担のない体へ。"]
            },
            {
                "start": 11.5,
                "end": 15.0,
                "tag": "公式ホームページ・施設情報",
                "lines": ["詳しくは", "プロフィールから"]
            }
        ]
    },
    {
        "theme_id": "theme_2_3",
        "category": "外来リハ",
        "title": "筋力だけではない体の使い方 #Shorts",
        "narration": "リハビリは、単に筋肉を鍛えるだけではありません。体が本来持っている、しなやかな動きを取り戻すことを目指します。",
        "scenes": [
            {
                "start": 0.0,
                "end": 11.5,
                "tag": "本来の動きを取り戻す",
                "lines": ["筋トレだけではない。", "本来の動きを引き出す。"]
            },
            {
                "start": 11.5,
                "end": 15.0,
                "tag": "公式ホームページ・施設情報",
                "lines": ["詳しくは", "プロフィールから"]
            }
        ]
    },

    # ----------------------------------------------------
    # 【テーマ3：通所リハ】
    # ----------------------------------------------------
    {
        "theme_id": "theme_3_1",
        "category": "通所リハ",
        "title": "退院後の体力づくり #Shorts",
        "narration": "退院したあとの生活も安心できるように。専門スタッフが体力の回復をサポートします。",
        "scenes": [
            {
                "start": 0.0,
                "end": 11.5,
                "tag": "退院後の安心サポート",
                "lines": ["退院後の生活を、", "無理のないリハビリで支える。"]
            },
            {
                "start": 11.5,
                "end": 15.0,
                "tag": "公式ホームページ・施設情報",
                "lines": ["詳しくは", "プロフィールから"]
            }
        ]
    },
    {
        "theme_id": "theme_3_2",
        "category": "通所リハ",
        "title": "専門職とつくる運動習慣 #Shorts",
        "narration": "一人での運動は、続けるのが難しいもの。あなたに合わせた個別プログラムで、無理なく楽しく継続できます。",
        "scenes": [
            {
                "start": 0.0,
                "end": 11.5,
                "tag": "通所リハビリの個別運動",
                "lines": ["個別のプログラムで、", "無理のない運動習慣を。"]
            },
            {
                "start": 11.5,
                "end": 15.0,
                "tag": "公式ホームページ・施設情報",
                "lines": ["詳しくは", "プロフィールから"]
            }
        ]
    },
    {
        "theme_id": "theme_3_3",
        "category": "通所リハ",
        "title": "家での動きを楽にするリハビリ #Shorts",
        "narration": "立ち上がりや階段の上り下り。日々の暮らしの動作がもっと楽になるよう、実践的なリハビリを行っています。",
        "scenes": [
            {
                "start": 0.0,
                "end": 11.5,
                "tag": "生活動作の改善",
                "lines": ["毎日の立ち上がりや階段を、", "もっと楽に。"]
            },
            {
                "start": 11.5,
                "end": 15.0,
                "tag": "公式ホームページ・施設情報",
                "lines": ["詳しくは", "プロフィールから"]
            }
        ]
    },

    # ----------------------------------------------------
    # 【テーマ4：通所介護】
    # ----------------------------------------------------
    {
        "theme_id": "theme_4_1",
        "category": "通所介護",
        "title": "日々の生活を元気にするデイサービス #Shorts",
        "narration": "体を動かし、仲間とおしゃべりを楽しむ。そんな時間が、毎日の元気を支えます。",
        "scenes": [
            {
                "start": 0.0,
                "end": 11.5,
                "tag": "リハビットセンターの日常",
                "lines": ["楽しく体を動かし、", "笑顔で過ごす場所。"]
            },
            {
                "start": 11.5,
                "end": 15.0,
                "tag": "公式ホームページ・施設情報",
                "lines": ["詳しくは", "プロフィールから"]
            }
        ]
    },
    {
        "theme_id": "theme_4_2",
        "category": "通所介護",
        "title": "体を動かす楽しさを取り戻す #Shorts",
        "narration": "運動に自信がない方でも安心です。一人ひとりのペースに合わせて、無理のない体操をサポートしています。",
        "scenes": [
            {
                "start": 0.0,
                "end": 11.5,
                "tag": "安心のデイサービス",
                "lines": ["無理のないペースで、", "体を動かす楽しさを。"]
            },
            {
                "start": 11.5,
                "end": 15.0,
                "tag": "公式ホームページ・施設情報",
                "lines": ["詳しくは", "プロフィールから"]
            }
        ]
    },
    {
        "theme_id": "theme_4_3",
        "category": "通所介護",
        "title": "無理のない運動と笑顔の時間 #Shorts",
        "narration": "外に出て誰かと話すこと。それだけで心も体も前向きになります。温かいスタッフと過ごす時間が、毎日の元気を支えます。",
        "scenes": [
            {
                "start": 0.0,
                "end": 11.5,
                "tag": "心と体のリフレッシュ",
                "lines": ["温かいスタッフと過ごす、", "安心の居場所。"]
            },
            {
                "start": 11.5,
                "end": 15.0,
                "tag": "公式ホームページ・施設情報",
                "lines": ["詳しくは", "プロフィールから"]
            }
        ]
    },

    # ----------------------------------------------------
    # 【テーマ5：ISR】
    # ----------------------------------------------------
    {
        "theme_id": "theme_5_1",
        "category": "ISR",
        "title": "筋肉の滑りをよくする手技 #Shorts",
        "narration": "筋肉の滑りを整える手技療法、アイエスアール。組織の癒着をゆるめ、スムーズな動きを目指します。",
        "scenes": [
            {
                "start": 0.0,
                "end": 11.5,
                "tag": "手技療法 ISR",
                "lines": ["筋肉の滑りを整え、", "動かしやすい体へ。"]
            },
            {
                "start": 11.5,
                "end": 15.0,
                "tag": "公式ホームページ・施設情報",
                "lines": ["詳しくは", "プロフィールから"]
            }
        ]
    },
    {
        "theme_id": "theme_5_2",
        "category": "ISR",
        "title": "動かしにくさの根本原因 #Shorts",
        "narration": "揉んでも戻る頑固な重だるさ。筋肉がスムーズに滑り合うよう、丁寧な手技で動きを整えます。",
        "scenes": [
            {
                "start": 0.0,
                "end": 11.5,
                "tag": "組織間リリースの効果",
                "lines": ["揉んでも戻る重だるさに。", "組織間リリース。"]
            },
            {
                "start": 11.5,
                "end": 15.0,
                "tag": "公式ホームページ・施設情報",
                "lines": ["詳しくは", "プロフィールから"]
            }
        ]
    },
    {
        "theme_id": "theme_5_3",
        "category": "ISR",
        "title": "関節の引っかかりを整える #Shorts",
        "narration": "腕を上げるときの違和感に。組織の滑りを整えて、無理のないスムーズな動きを目指します。",
        "scenes": [
            {
                "start": 0.0,
                "end": 11.5,
                "tag": "関節の引っかかり改善",
                "lines": ["動かすときの違和感を、", "スムーズに整える。"]
            },
            {
                "start": 11.5,
                "end": 15.0,
                "tag": "公式ホームページ・施設情報",
                "lines": ["詳しくは", "プロフィールから"]
            }
        ]
    },

    # ----------------------------------------------------
    # 【テーマ6：レッドコード】
    # ----------------------------------------------------
    {
        "theme_id": "theme_6_1",
        "category": "レッドコード",
        "title": "赤いロープで体を支える運動 #Shorts",
        "narration": "天井から吊るされた赤いロープ。体重をやさしく支えるため、膝や腰に無理な力をかけずに運動できます。",
        "scenes": [
            {
                "start": 0.0,
                "end": 11.5,
                "tag": "レッドコード訓練",
                "lines": ["赤いロープで体を支え、", "負担なく運動。"]
            },
            {
                "start": 11.5,
                "end": 15.0,
                "tag": "公式ホームページ・施設情報",
                "lines": ["詳しくは", "プロフィールから"]
            }
        ]
    },
    {
        "theme_id": "theme_6_2",
        "category": "レッドコード",
        "title": "自重を使った無理のない体幹訓練 #Shorts",
        "narration": "自分の体重を利用してバランスを整えるレッドコード。体の奥の筋肉を刺激して、ふらつきにくい安定した姿勢をつくります。",
        "scenes": [
            {
                "start": 0.0,
                "end": 11.5,
                "tag": "体幹バランス訓練",
                "lines": ["自分の体重を活かし、", "体幹バランスを整える。"]
            },
            {
                "start": 11.5,
                "end": 15.0,
                "tag": "公式ホームページ・施設情報",
                "lines": ["詳しくは", "プロフィールから"]
            }
        ]
    },
    {
        "theme_id": "theme_6_3",
        "category": "レッドコード",
        "title": "体のバランスを整える浮遊感 #Shorts",
        "narration": "ロープに体を預ける心地よい感覚。余分な力を抜きながら、バランスの良い姿勢を取り戻していきます。",
        "scenes": [
            {
                "start": 0.0,
                "end": 11.5,
                "tag": "リラックスと正しい姿勢",
                "lines": ["余分な緊張をほぐし、", "正しい姿勢を体に。"]
            },
            {
                "start": 11.5,
                "end": 15.0,
                "tag": "公式ホームページ・施設情報",
                "lines": ["詳しくは", "プロフィールから"]
            }
        ]
    },

    # ----------------------------------------------------
    # 【テーマ7：小規模多機能】
    # ----------------------------------------------------
    {
        "theme_id": "theme_7_1",
        "category": "小規模多機能",
        "title": "通い・泊まり・訪問をひとつに #Shorts",
        "narration": "デイサービスも、ショートステイも、訪問も。いつも同じスタッフが支える安心があります。",
        "scenes": [
            {
                "start": 0.0,
                "end": 11.5,
                "tag": "小規模多機能センター",
                "lines": ["通い・泊まり・訪問。", "顔なじみの安心を。"]
            },
            {
                "start": 11.5,
                "end": 15.0,
                "tag": "公式ホームページ・施設情報",
                "lines": ["詳しくは", "プロフィールから"]
            }
        ]
    },
    {
        "theme_id": "theme_7_2",
        "category": "小規模多機能",
        "title": "住み慣れた自宅で暮らし続ける #Shorts",
        "narration": "住み慣れた家でずっと暮らしたい。その想いに寄り添い、状態の変化に合わせて柔軟に生活をサポートします。",
        "scenes": [
            {
                "start": 0.0,
                "end": 11.5,
                "tag": "在宅生活の継続支援",
                "lines": ["住み慣れた家で、", "安心して暮らし続ける。"]
            },
            {
                "start": 11.5,
                "end": 15.0,
                "tag": "公式ホームページ・施設情報",
                "lines": ["詳しくは", "プロフィールから"]
            }
        ]
    },
    {
        "theme_id": "theme_7_3",
        "category": "小規模多機能",
        "title": "環境を変えずに支える介護 #Shorts",
        "narration": "場所や人が変わると不安になりやすい介護。いつも同じスタッフがそばにいることで、心から安心できる居場所をつくります。",
        "scenes": [
            {
                "start": 0.0,
                "end": 11.5,
                "tag": "継続する安心サポート",
                "lines": ["いつも同じスタッフだから、", "心穏やかに。"]
            },
            {
                "start": 11.5,
                "end": 15.0,
                "tag": "公式ホームページ・施設情報",
                "lines": ["詳しくは", "プロフィールから"]
            }
        ]
    }
]

DEFAULT_THEME = THEMES[0]

def get_theme_by_id(theme_id: str):
    for t in THEMES:
        if t["theme_id"] == theme_id:
            return t
    return None

def get_all_themes():
    return THEMES

def select_next_theme(state_file="state/theme_state.json"):
    """
    次のテーマを選択して返す（状態ファイルへの書き込みは行わない読み込み専用関数）。
    - 環境変数 THEME_ID が指定されている場合は最優先でそのテーマを返す。
    - 状態ファイルが存在しない場合: THEMES[0] (theme_1_1) を選択。
    - 状態ファイルに前回のテーマ情報がある場合: 次のテーマを選択。
    - theme_7_3 (21番目) の次は theme_1_1 (1番目) へ戻る。
    - 読み込みエラー時は安全に DEFAULT_THEME を返す。
    """
    # 1. 環境変数 THEME_ID の優先処理
    env_theme_id = os.environ.get("THEME_ID", "").strip()
    if env_theme_id:
        theme = get_theme_by_id(env_theme_id)
        if theme:
            return theme
        else:
            print(f"[THEME WARNING] Specified THEME_ID '{env_theme_id}' not found. Falling back to DEFAULT_THEME.")
            return DEFAULT_THEME

    # 2. 状態ファイルからの前回情報読み込み
    next_index = 0
    try:
        if os.path.exists(state_file):
            with open(state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            last_theme_id = data.get("last_theme_id", "")
            for idx, t in enumerate(THEMES):
                if t["theme_id"] == last_theme_id:
                    next_index = (idx + 1) % len(THEMES)
                    break
    except Exception as e:
        print(f"[THEME WARNING] Failed to read state file '{state_file}': {e}. Using DEFAULT_THEME.")
        return DEFAULT_THEME

    return THEMES[next_index]

def commit_theme_state(theme_or_id, state_file="state/theme_state.json"):
    """
    YouTube投稿成功後に明示的に呼び出され、テーマ状態を確定保存する関数。
    """
    if isinstance(theme_or_id, dict):
        theme_id = theme_or_id.get("theme_id", "")
    else:
        theme_id = str(theme_or_id)

    theme = get_theme_by_id(theme_id)
    if not theme:
        theme = DEFAULT_THEME
        theme_id = theme["theme_id"]

    try:
        theme_index = THEMES.index(theme)
    except ValueError:
        theme_index = 0

    try:
        os.makedirs(os.path.dirname(os.path.abspath(state_file)), exist_ok=True)
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump({
                "last_theme_id": theme_id,
                "last_index": theme_index,
                "category": theme.get("category", ""),
                "title": theme.get("title", "")
            }, f, ensure_ascii=False, indent=2)
        print(f"[THEME STATE] Successfully committed theme state: {theme_id} ({theme.get('title', '')})")
        return True
    except Exception as e:
        print(f"[THEME WARNING] Failed to commit state file '{state_file}': {e}.")
        return False

def get_next_theme(state_file="state/theme_state.json", auto_commit=True):
    """
    確定済み21テーマの自動ローテーション選択関数（後方互換性用）。
    auto_commit=True の場合は即座に状態を保存、False の場合は選択のみ。
    """
    selected_theme = select_next_theme(state_file=state_file)
    if auto_commit:
        commit_theme_state(selected_theme, state_file=state_file)
    return selected_theme
