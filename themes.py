import os
import json
import random

STATE_FILE_PATH = os.path.join(os.path.dirname(__file__), 'state', 'theme_state.json')
TEST_STATE_FILE_PATH = os.path.join(os.path.dirname(__file__), 'state', 'test_theme_state.json')

CTA_VARIATIONS = [
    "詳しくはプロフィールへ。",
    "気になる方はプロフィールをご覧ください。",
    "詳しくはプロフィールからご確認ください。",
    "西田医院の取り組みはプロフィールから。"
]

THEMES = [
    # =========================================================================
    # カテゴリー1: 理念・全体方針 (全3本)
    # =========================================================================
    {
        "theme_id": "theme_1_1",
        "category": "理念",
        "title": "痛みの先にある生活 #Shorts",
        "variations": [
            {
                "pattern_id": "PATTERN_SURPRISE",
                "hook_type": "SURPRISE",
                "structure_type": "HOOK → EXPLANATION → CTA",
                "angle": "痛みの緩和はゴールではなく生活再建のスタートという視点",
                "narration_template": "痛みを和らげること。それはゴールではなく、スタートです。西田医院では、あなたが笑顔で暮らせるよう一緒に考えます。{cta}",
                "bg_query": "medical consultation doctor clinic",
                "bg_queries": [
                    "medical consultation doctor clinic",
                    "doctor talking with senior patient clinic",
                    "healthcare professional consulting elderly"
                ]
            },
            {
                "pattern_id": "PATTERN_QUESTION",
                "hook_type": "QUESTION",
                "structure_type": "QUESTION → REASON → CTA",
                "angle": "痛みがなくなった後の理想の暮らしに問いかける視点",
                "narration_template": "痛みが軽くなったら、どんな毎日を過ごしたいですか？西田医院は、あなたが笑顔で暮らす未来を一緒にサポートします。{cta}",
                "bg_query": "senior smiling doctor consultation",
                "bg_queries": [
                    "senior smiling doctor consultation",
                    "elderly woman talking happily doctor",
                    "senior patient consultation clinic"
                ]
            },
            {
                "pattern_id": "PATTERN_BENEFIT",
                "hook_type": "BENEFIT",
                "structure_type": "BENEFIT → METHOD → CTA",
                "angle": "生活背景まで見つめる医療がもたらす安心感",
                "narration_template": "治療の先にある、生き生きとした暮らしを支えたい。生活の背景まで丁寧に見つめ、寄り添う医療を届けます。{cta}",
                "bg_query": "doctor listening patient clinic",
                "bg_queries": [
                    "doctor listening patient clinic",
                    "caring doctor consultation senior",
                    "warm healthcare clinic consultation"
                ]
            }
        ]
    },
    {
        "theme_id": "theme_1_2",
        "category": "理念",
        "title": "医療と介護をつなぐ理由 #Shorts",
        "variations": [
            {
                "pattern_id": "PATTERN_SURPRISE",
                "hook_type": "SURPRISE",
                "structure_type": "HOOK → EXPLANATION → CTA",
                "angle": "医療単体では支えきれない日常を介護と一体化する視点",
                "narration_template": "医療だけでは生活を支えきれません。だから私たちは、医療と介護をひとつにつなげています。{cta}",
                "bg_query": "doctor with senior patient care",
                "bg_queries": [
                    "doctor with senior patient care",
                    "medical staff healthcare team smiling",
                    "caregiver and doctor teamwork"
                ]
            },
            {
                "pattern_id": "PATTERN_QUESTION",
                "hook_type": "QUESTION",
                "structure_type": "QUESTION → REASON → CTA",
                "angle": "退院後の暮らしの不安と切れ目のない支援",
                "narration_template": "退院した後の暮らしに不安はありませんか？医療と介護が連携し、日々の生活を途切れなく支えます。{cta}",
                "bg_query": "caregiver helping elderly person home",
                "bg_queries": [
                    "caregiver helping elderly person home",
                    "nurse supporting senior patient room",
                    "healthcare provider visiting elderly"
                ]
            },
            {
                "pattern_id": "PATTERN_EMPATHY",
                "hook_type": "EMPATHY",
                "structure_type": "PROBLEM → SOLUTION → CTA",
                "angle": "専門職チームによる安心の生活防衛",
                "narration_template": "体の治療から毎日の生活サポートまで。医療と介護の専門職がチームとなり、あなたらしい暮らしを守ります。{cta}",
                "bg_query": "medical staff healthcare team smiling",
                "bg_queries": [
                    "medical staff healthcare team smiling",
                    "nurse and physical therapist clinic",
                    "interprofessional care team hospital"
                ]
            }
        ]
    },
    {
        "theme_id": "theme_1_3",
        "category": "理念",
        "title": "自分の足で歩き続けるために #Shorts",
        "variations": [
            {
                "pattern_id": "PATTERN_BENEFIT",
                "hook_type": "BENEFIT",
                "structure_type": "BENEFIT → METHOD → CTA",
                "angle": "生涯自分の足で歩くための早期予防と運動",
                "narration_template": "いくつになっても自分の足で歩きたい。その願いを支えるため、日々の予防と運動をサポートしています。{cta}",
                "bg_query": "senior walking outside happily",
                "bg_queries": [
                    "senior walking outside happily",
                    "elderly couple walking park sunlight",
                    "senior feet walking grass healthy"
                ]
            },
            {
                "pattern_id": "PATTERN_QUESTION",
                "hook_type": "QUESTION",
                "structure_type": "QUESTION → REASON → CTA",
                "angle": "歩行スピードの低下への気づきと足腰づくり",
                "narration_template": "最近、歩くスピードが遅くなったと感じていませんか？日々の無理のない運動で、歩き続けられる足腰をつくります。{cta}",
                "bg_query": "elderly walking exercise park",
                "bg_queries": [
                    "elderly walking exercise park",
                    "senior walking path nature",
                    "elderly fitness walking outdoors"
                ]
            },
            {
                "pattern_id": "PATTERN_SCENE",
                "hook_type": "SCENE",
                "structure_type": "SCENE → INSIGHT → CTA",
                "angle": "行きたい場所へ自由に出かけられる喜びの維持",
                "narration_template": "行きたい場所へ自分で行ける喜びをずっと。早期の予防と丁寧なリハビリで、確かな一歩を支え続けます。{cta}",
                "bg_query": "senior feet walking grass healthy",
                "bg_queries": [
                    "senior feet walking grass healthy",
                    "active senior walking trail",
                    "elderly walking city morning"
                ]
            }
        ]
    },

    # =========================================================================
    # カテゴリー2: 外来リハビリ (全3本)
    # =========================================================================
    {
        "theme_id": "theme_2_1",
        "category": "外来リハ",
        "title": "痛む場所だけを見ないリハビリ #Shorts",
        "variations": [
            {
                "pattern_id": "PATTERN_SURPRISE",
                "hook_type": "SURPRISE",
                "structure_type": "HOOK → EXPLANATION → CTA",
                "angle": "膝の痛みの原因が膝以外にあるという逆張り視点",
                "narration_template": "膝の痛み、実は膝以外に原因があるかも？西田医院では体全体のバランスを丁寧に評価します。{cta}",
                "bg_query": "physical therapy rehabilitation exercise",
                "bg_queries": [
                    "physical therapy rehabilitation exercise",
                    "physiotherapist examining knee joint",
                    "physical therapist posture balance test"
                ]
            },
            {
                "pattern_id": "PATTERN_COMMON_MISTAKE",
                "hook_type": "COMMON_MISTAKE",
                "structure_type": "COMMON_MISTAKE → CORRECTION → CTA",
                "angle": "痛む局所ばかり気にして全体を見落とす誤解の解消",
                "narration_template": "膝が痛いとき、膝ばかり気にしていませんか？骨盤や足首の歪みまで見極め、根本的な動きを整えます。{cta}",
                "bg_query": "physiotherapist examining knee joint",
                "bg_queries": [
                    "physiotherapist examining knee joint",
                    "doctor examining patient joint pain",
                    "physical therapist checking leg alignment"
                ]
            },
            {
                "pattern_id": "PATTERN_EMPATHY",
                "hook_type": "EMPATHY",
                "structure_type": "PROBLEM → SOLUTION → CTA",
                "angle": "湿布では治まらない違和感への全身評価アプローチ",
                "narration_template": "湿布を貼っても戻る関節の違和感に。体全体のバランスを細かくチェックし、痛みの根本にアプローチします。{cta}",
                "bg_query": "physical therapist posture balance test",
                "bg_queries": [
                    "physical therapist posture balance test",
                    "physiotherapy posture assessment clinic",
                    "rehabilitation therapist checking patient balance"
                ]
            }
        ]
    },
    {
        "theme_id": "theme_2_2",
        "category": "外来リハ",
        "title": "姿勢と歩き方の見直し #Shorts",
        "variations": [
            {
                "pattern_id": "PATTERN_QUESTION",
                "hook_type": "QUESTION",
                "structure_type": "QUESTION → REASON → CTA",
                "angle": "歩き方のクセが関節負担を生んでいる気づき",
                "narration_template": "歩き方のクセ、放っておいていませんか？理学療法士と一緒に、無理のない体の動かし方を練習します。{cta}",
                "bg_query": "physiotherapy walking posture balance",
                "bg_queries": [
                    "physiotherapy walking posture balance",
                    "physical therapist correcting gait posture",
                    "senior walking test clinic physiotherapy"
                ]
            },
            {
                "pattern_id": "PATTERN_SURPRISE",
                "hook_type": "SURPRISE",
                "structure_type": "HOOK → EXPLANATION → CTA",
                "angle": "無意識の歩行習慣が関節痛を引き起こすメカニズム",
                "narration_template": "無意識の歩き方のクセが、膝や腰の負担に。理学療法士が姿勢を整え、スムーズな歩き方をサポートします。{cta}",
                "bg_query": "physical therapist correcting gait posture",
                "bg_queries": [
                    "physical therapist correcting gait posture",
                    "gait analysis physical therapy room",
                    "patient walking rehabilitation parallel bars"
                ]
            },
            {
                "pattern_id": "PATTERN_SCENE",
                "hook_type": "SCENE",
                "structure_type": "SCENE → INSIGHT → CTA",
                "angle": "靴の減り方の偏りから見直す関節保護の歩行",
                "narration_template": "靴の減り方に左右差はありませんか？歩く姿勢をプロが見直すことで、関節への負担をやわらげます。{cta}",
                "bg_query": "senior walking test clinic physiotherapy",
                "bg_queries": [
                    "senior walking test clinic physiotherapy",
                    "elderly person walking gait clinic",
                    "physiotherapist watching patient walk"
                ]
            }
        ]
    },
    {
        "theme_id": "theme_2_3",
        "category": "外来リハ",
        "title": "筋力だけではない体の使い方 #Shorts",
        "variations": [
            {
                "pattern_id": "PATTERN_COMMON_MISTAKE",
                "hook_type": "COMMON_MISTAKE",
                "structure_type": "COMMON_MISTAKE → CORRECTION → CTA",
                "angle": "リハビリ＝単なる筋トレという誤解の解消",
                "narration_template": "リハビリは筋トレだけではありません。体が本来持っている、しなやかな動きを取り戻しましょう。{cta}",
                "bg_query": "physiotherapist assisting patient exercise",
                "bg_queries": [
                    "physiotherapist assisting patient exercise",
                    "patient stretching rehabilitation physical therapy",
                    "physiotherapy gentle movement therapy"
                ]
            },
            {
                "pattern_id": "PATTERN_QUESTION",
                "hook_type": "QUESTION",
                "structure_type": "QUESTION → REASON → CTA",
                "angle": "筋肉を鍛えても取れない動かしにくさの原因",
                "narration_template": "筋肉を鍛えても動きにくさが残っていませんか？関節が滑らかに連動する、無理のない体の使い方を身につけます。{cta}",
                "bg_query": "patient stretching rehabilitation physical therapy",
                "bg_queries": [
                    "patient stretching rehabilitation physical therapy",
                    "gentle joint mobility exercise clinic",
                    "physical therapy flexibility movement"
                ]
            },
            {
                "pattern_id": "PATTERN_BENEFIT",
                "hook_type": "BENEFIT",
                "structure_type": "BENEFIT → METHOD → CTA",
                "angle": "力任せではない省エネで楽な動作の再学習",
                "narration_template": "力任せではない、楽な動き方を覚えること。体の連動性を引き出し、毎日の動作を快適に整えます。{cta}",
                "bg_query": "physiotherapy gentle movement therapy",
                "bg_queries": [
                    "physiotherapy gentle movement therapy",
                    "rehabilitation coordination movement practice",
                    "smooth body movement exercise physical therapy"
                ]
            }
        ]
    },

    # =========================================================================
    # カテゴリー3: 通所リハビリ (全3本)
    # =========================================================================
    {
        "theme_id": "theme_3_1",
        "category": "通所リハ",
        "title": "退院後の体力づくり #Shorts",
        "variations": [
            {
                "pattern_id": "PATTERN_QUESTION",
                "hook_type": "QUESTION",
                "structure_type": "QUESTION → REASON → CTA",
                "angle": "退院後の生活や体力低下への不安への問いかけ",
                "narration_template": "退院したあとの体力、不安はありませんか？専門スタッフが一人ひとりの回復をサポートします。{cta}",
                "bg_query": "rehabilitation senior walking clinic",
                "bg_queries": [
                    "rehabilitation senior walking clinic",
                    "elderly rehab exercise parallel bars",
                    "physiotherapist guiding senior patient gym"
                ]
            },
            {
                "pattern_id": "PATTERN_EMPATHY",
                "hook_type": "EMPATHY",
                "structure_type": "PROBLEM → SOLUTION → CTA",
                "angle": "入院で落ちた体力を段階的に回復するステップ",
                "narration_template": "入院生活で落ちてしまった体力を取り戻すために。無理のない段階的なリハビリで、安心の日常へつなげます。{cta}",
                "bg_query": "elderly rehab exercise parallel bars",
                "bg_queries": [
                    "elderly rehab exercise parallel bars",
                    "senior walking rehab parallel bar training",
                    "elderly recovery rehabilitation clinic"
                ]
            },
            {
                "pattern_id": "PATTERN_BENEFIT",
                "hook_type": "BENEFIT",
                "structure_type": "BENEFIT → METHOD → CTA",
                "angle": "理学療法士常駐デイケアによる着実な回復",
                "narration_template": "退院後も自分らしく動ける体づくりを。理学療法士が常駐するデイケアで、着実な体力回復を応援します。{cta}",
                "bg_query": "physiotherapist guiding senior patient gym",
                "bg_queries": [
                    "physiotherapist guiding senior patient gym",
                    "senior rehabilitation fitness clinic",
                    "physical therapist instructing senior exercise"
                ]
            }
        ]
    },
    {
        "theme_id": "theme_3_2",
        "category": "通所リハ",
        "title": "専門職とつくる運動習慣 #Shorts",
        "variations": [
            {
                "pattern_id": "PATTERN_EMPATHY",
                "hook_type": "EMPATHY",
                "structure_type": "PROBLEM → SOLUTION → CTA",
                "angle": "一人では続かない運動を個別プログラムで楽しく継続",
                "narration_template": "運動が続かないとお悩みの方へ。あなたに合わせた個別プログラムで無理なく楽しく継続できます。{cta}",
                "bg_query": "elderly stretching exercise health",
                "bg_queries": [
                    "elderly stretching exercise health",
                    "senior group exercise physical therapy",
                    "elderly stretching trainer clinic"
                ]
            },
            {
                "pattern_id": "PATTERN_QUESTION",
                "hook_type": "QUESTION",
                "structure_type": "QUESTION → REASON → CTA",
                "angle": "自主トレが三日坊主になりやすい悩みへのアプローチ",
                "narration_template": "家での運動、ついつい後回しになっていませんか？専門職のサポートで、楽しく続けられる運動習慣を始めましょう。{cta}",
                "bg_query": "senior group exercise physical therapy",
                "bg_queries": [
                    "senior group exercise physical therapy",
                    "group stretching session elderly",
                    "senior fitness class healthcare clinic"
                ]
            },
            {
                "pattern_id": "PATTERN_BENEFIT",
                "hook_type": "BENEFIT",
                "structure_type": "BENEFIT → METHOD → CTA",
                "angle": "プロの個別指導による安心安全な体力向上",
                "narration_template": "一人では不安な運動も、プロと一緒なら安心。あなたのペースに合わせた指導で、動ける体を育みます。{cta}",
                "bg_query": "elderly stretching trainer clinic",
                "bg_queries": [
                    "elderly stretching trainer clinic",
                    "trainer helping senior stretch clinic",
                    "personalized exercise rehabilitation senior"
                ]
            }
        ]
    },
    {
        "theme_id": "theme_3_3",
        "category": "通所リハ",
        "title": "家での動きを楽にするリハビリ #Shorts",
        "variations": [
            {
                "pattern_id": "PATTERN_SCENE",
                "hook_type": "SCENE",
                "structure_type": "SCENE → INSIGHT → CTA",
                "angle": "階段や立ち上がりなど日常動作に直結するリハビリ",
                "narration_template": "階段の上り下り、つらくなっていませんか？日々の暮らしの動作がもっと楽になるリハビリを行っています。{cta}",
                "bg_query": "senior walking stairs rehabilitation",
                "bg_queries": [
                    "senior walking stairs rehabilitation",
                    "elderly person standing up chair exercise",
                    "rehabilitation clinic indoor mobility test"
                ]
            },
            {
                "pattern_id": "PATTERN_EMPATHY",
                "hook_type": "EMPATHY",
                "structure_type": "PROBLEM → SOLUTION → CTA",
                "angle": "椅子からの立ち上がりや段差移動の実践練習",
                "narration_template": "椅子からの立ち上がりや段差の移動。毎日の暮らしの中でつまずきやすい動きを、実践的に練習します。{cta}",
                "bg_query": "elderly person standing up chair exercise",
                "bg_queries": [
                    "elderly person standing up chair exercise",
                    "senior chair stand test rehabilitation",
                    "functional mobility training senior clinic"
                ]
            },
            {
                "pattern_id": "PATTERN_BENEFIT",
                "hook_type": "BENEFIT",
                "structure_type": "BENEFIT → METHOD → CTA",
                "angle": "自宅環境を想定した生活直結型リハビリテーション",
                "narration_template": "ご自宅で安心して暮らし続けるために。実際の生活環境を想定したリハビリで、日常の動きをスムーズに整えます。{cta}",
                "bg_query": "rehabilitation clinic indoor mobility test",
                "bg_queries": [
                    "rehabilitation clinic indoor mobility test",
                    "home environment mobility training rehab",
                    "practical physical therapy daily activities"
                ]
            }
        ]
    },

    # =========================================================================
    # カテゴリー4: 通所介護 (デイサービス) (全3本)
    # =========================================================================
    {
        "theme_id": "theme_4_1",
        "category": "通所介護",
        "title": "日々の生活を元気にするデイサービス #Shorts",
        "variations": [
            {
                "pattern_id": "PATTERN_QUESTION",
                "hook_type": "QUESTION",
                "structure_type": "QUESTION → REASON → CTA",
                "angle": "外出とおしゃべりがもたらす毎日の活力",
                "narration_template": "最近、外に出て誰かと笑い合っていますか？体を動かし仲間と過ごす時間が毎日の元気を支えます。{cta}",
                "bg_query": "elderly people smiling social care",
                "bg_queries": [
                    "elderly people smiling social care",
                    "senior group smiling talking daycare",
                    "elderly activity center laughing"
                ]
            },
            {
                "pattern_id": "PATTERN_EMPATHY",
                "hook_type": "EMPATHY",
                "structure_type": "PROBLEM → SOLUTION → CTA",
                "angle": "閉じこもりがちな日常を明るい交流で変える",
                "narration_template": "一日中家にいると気分も沈みがちに。温かい仲間とおしゃべりや体操を楽しみ、心弾む毎日をつくりましょう。{cta}",
                "bg_query": "senior group smiling talking daycare",
                "bg_queries": [
                    "senior group smiling talking daycare",
                    "elderly friends chatting cafe daycare",
                    "cheerful senior daycare recreation"
                ]
            },
            {
                "pattern_id": "PATTERN_BENEFIT",
                "hook_type": "BENEFIT",
                "structure_type": "BENEFIT → METHOD → CTA",
                "angle": "通うのが楽しみになるコミュニティと健康づくり",
                "narration_template": "通うのが楽しみになる場所をめざして。無理のない運動と笑顔あふれる交流が、元気の秘訣です。{cta}",
                "bg_query": "elderly activity center laughing",
                "bg_queries": [
                    "elderly activity center laughing",
                    "senior recreation activity daycare",
                    "happy elderly people community clinic"
                ]
            }
        ]
    },
    {
        "theme_id": "theme_4_2",
        "category": "通所介護",
        "title": "体を動かす楽しさを取り戻す #Shorts",
        "variations": [
            {
                "pattern_id": "PATTERN_BENEFIT",
                "hook_type": "BENEFIT",
                "structure_type": "BENEFIT → METHOD → CTA",
                "angle": "運動が苦手な方でも安心の個別ペース体操",
                "narration_template": "運動に自信がなくても大丈夫。一人ひとりのペースに合わせて、無理のない体操をサポートしています。{cta}",
                "bg_query": "senior group exercise fun",
                "bg_queries": [
                    "senior group exercise fun",
                    "elderly chair exercise stretching",
                    "senior people gentle stretching smiling"
                ]
            },
            {
                "pattern_id": "PATTERN_QUESTION",
                "hook_type": "QUESTION",
                "structure_type": "QUESTION → REASON → CTA",
                "angle": "体が硬い・ついていけない不安への座ったまま体操",
                "narration_template": "体が硬くて体操についていけるか不安ですか？座ったままできる簡単な運動で、気持ちよく体をほぐします。{cta}",
                "bg_query": "elderly chair exercise stretching",
                "bg_queries": [
                    "elderly chair exercise stretching",
                    "seated gentle stretching senior daycare",
                    "chair yoga elderly stretching exercise"
                ]
            },
            {
                "pattern_id": "PATTERN_EMPATHY",
                "hook_type": "EMPATHY",
                "structure_type": "PROBLEM → SOLUTION → CTA",
                "angle": "動かす心地よさをスタッフの声かけで取り戻す",
                "narration_template": "体を動かす心地よさをもう一度。スタッフの温かい声かけと一緒に、笑顔でできる体操を始めましょう。{cta}",
                "bg_query": "senior people gentle stretching smiling",
                "bg_queries": [
                    "senior people gentle stretching smiling",
                    "caregiver encouraging senior stretching",
                    "pleasant gentle exercise senior center"
                ]
            }
        ]
    },
    {
        "theme_id": "theme_4_3",
        "category": "通所介護",
        "title": "無理のない運動と笑顔の時間 #Shorts",
        "variations": [
            {
                "pattern_id": "PATTERN_SURPRISE",
                "hook_type": "SURPRISE",
                "structure_type": "HOOK → EXPLANATION → CTA",
                "angle": "会話と笑顔そのものが心身の前向きな活力になる",
                "narration_template": "誰かと話すだけで心も体も前向きに。温かいスタッフと過ごす時間が、毎日の笑顔をつくります。{cta}",
                "bg_query": "senior people talking laughing cafe",
                "bg_queries": [
                    "senior people talking laughing cafe",
                    "caregiver chatting with senior smiling",
                    "senior daycare social interaction"
                ]
            },
            {
                "pattern_id": "PATTERN_QUESTION",
                "hook_type": "QUESTION",
                "structure_type": "QUESTION → REASON → CTA",
                "angle": "会話の減少と孤立を防ぐ安心の居場所",
                "narration_template": "人と話す機会が減ったと感じていませんか？笑顔が交わい温かい会話が生まれる、安心の居場所があります。{cta}",
                "bg_query": "caregiver chatting with senior smiling",
                "bg_queries": [
                    "caregiver chatting with senior smiling",
                    "kind nurse listening senior talking",
                    "warm conversation senior daycare"
                ]
            },
            {
                "pattern_id": "PATTERN_EMPATHY",
                "hook_type": "EMPATHY",
                "structure_type": "PROBLEM → SOLUTION → CTA",
                "angle": "心を通わせるケアが育む日々の安心と幸福感",
                "narration_template": "心を通わせる時間が、何よりの元気の源。一人ひとりに寄り添い、安心と楽しさに満ちた時間を届けます。{cta}",
                "bg_query": "senior daycare social interaction",
                "bg_queries": [
                    "senior daycare social interaction",
                    "senior community center happy atmosphere",
                    "friendly caregiver and senior resident"
                ]
            }
        ]
    },

    # =========================================================================
    # カテゴリー5: ISR (組織間リリース) (全3本)
    # =========================================================================
    {
        "theme_id": "theme_5_1",
        "category": "ISR",
        "title": "筋肉の滑りをよくする手技 #Shorts",
        "variations": [
            {
                "pattern_id": "PATTERN_SCENE",
                "hook_type": "SCENE",
                "structure_type": "SCENE → INSIGHT → CTA",
                "angle": "頑固なコリや引っかかりに対する組織間リリース手技",
                "narration_template": "頑固なコリや動かしにくさに。筋肉の滑りを整える手技療法、アイエスアールでスムーズな動きへ。{cta}",
                "bg_query": "physical therapist manual therapy massage",
                "bg_queries": [
                    "physical therapist manual therapy massage",
                    "physiotherapist manual joint release",
                    "physical therapy shoulder manual treatment"
                ]
            },
            {
                "pattern_id": "PATTERN_QUESTION",
                "hook_type": "QUESTION",
                "structure_type": "QUESTION → REASON → CTA",
                "angle": "筋肉のつっぱり感と組織癒着のメカニズム",
                "narration_template": "筋肉が突っ張るような違和感はありませんか？癒着した組織同士の滑りをやさしくゆるめ、可動域を広げます。{cta}",
                "bg_query": "physiotherapist manual joint release",
                "bg_queries": [
                    "physiotherapist manual joint release",
                    "physical therapist fascia release technique",
                    "manual physical therapy soft tissue clinic"
                ]
            },
            {
                "pattern_id": "PATTERN_BENEFIT",
                "hook_type": "BENEFIT",
                "structure_type": "BENEFIT → METHOD → CTA",
                "angle": "徒手アプローチによる関節本来のしなやかさ回復",
                "narration_template": "引っかかりのない滑らかな関節の動きを。丁寧な徒手アプローチで、組織本来のしなやかさを取り戻します。{cta}",
                "bg_query": "physical therapy shoulder manual treatment",
                "bg_queries": [
                    "physical therapy shoulder manual treatment",
                    "gentle manual joint mobilization",
                    "specialist therapist joint treatment"
                ]
            }
        ]
    },
    {
        "theme_id": "theme_5_2",
        "category": "ISR",
        "title": "動かしにくさの根本原因 #Shorts",
        "variations": [
            {
                "pattern_id": "PATTERN_COMMON_MISTAKE",
                "hook_type": "COMMON_MISTAKE",
                "structure_type": "COMMON_MISTAKE → CORRECTION → CTA",
                "angle": "揉んでも戻る重だるさの根本原因は組織の滑走性不足",
                "narration_template": "揉んでもすぐに戻る重だるさ。組織同士が滑り合うよう丁寧な手技で動きの根本を整えます。{cta}",
                "bg_query": "doctor examining patient joint pain",
                "bg_queries": [
                    "doctor examining patient joint pain",
                    "physiotherapist palpation spine back",
                    "physical therapy neck massage examination"
                ]
            },
            {
                "pattern_id": "PATTERN_QUESTION",
                "hook_type": "QUESTION",
                "structure_type": "QUESTION → REASON → CTA",
                "angle": "マッサージ直後しか効果が続かない悩みへの答え",
                "narration_template": "マッサージを受けてもすぐコリが戻りませんか？筋肉の滑走性を引き出すことで、動きやすさが長持ちします。{cta}",
                "bg_query": "physiotherapist palpation spine back",
                "bg_queries": [
                    "physiotherapist palpation spine back",
                    "physical therapist evaluating back muscles",
                    "back pain examination physiotherapy"
                ]
            },
            {
                "pattern_id": "PATTERN_SURPRISE",
                "hook_type": "SURPRISE",
                "structure_type": "HOOK → EXPLANATION → CTA",
                "angle": "組織の癒着が重だるさを生む意外な事実と専門手技",
                "narration_template": "重だるさの原因は組織の癒着にあることも。滑りを整える専門手技で、軽やかな体の感覚へ導きます。{cta}",
                "bg_query": "physical therapy neck massage examination",
                "bg_queries": [
                    "physical therapy neck massage examination",
                    "neck pain manual therapy physical therapist",
                    "gentle myofascial release therapist"
                ]
            }
        ]
    },
    {
        "theme_id": "theme_5_3",
        "category": "ISR",
        "title": "関節の引っかかりを整える #Shorts",
        "variations": [
            {
                "pattern_id": "PATTERN_SCENE",
                "hook_type": "SCENE",
                "structure_type": "SCENE → INSIGHT → CTA",
                "angle": "腕を上げる瞬間の違和感と滑走性の改善",
                "narration_template": "腕を上げるときの引っかかり感に。組織の滑りを整えて、無理のないスムーズな動きを目指します。{cta}",
                "bg_query": "physiotherapist stretching patient shoulder",
                "bg_queries": [
                    "physiotherapist stretching patient shoulder",
                    "doctor examining senior shoulder mobility",
                    "physical therapist stretching arms therapy"
                ]
            },
            {
                "pattern_id": "PATTERN_QUESTION",
                "hook_type": "QUESTION",
                "structure_type": "QUESTION → REASON → CTA",
                "angle": "肩を回したときの途中の引っかかりと組織解放",
                "narration_template": "肩を回すと途中で引っかかる感じはありませんか？関節周囲の組織を解放し、自然な腕の上り下りを整えます。{cta}",
                "bg_query": "doctor examining senior shoulder mobility",
                "bg_queries": [
                    "doctor examining senior shoulder mobility",
                    "shoulder range of motion test clinic",
                    "senior patient shoulder examination"
                ]
            },
            {
                "pattern_id": "PATTERN_EMPATHY",
                "hook_type": "EMPATHY",
                "structure_type": "PROBLEM → SOLUTION → CTA",
                "angle": "着替え動作時の違和感と摩擦低減アプローチ",
                "narration_template": "服を着替えるときの肩の違和感に。組織間の摩擦を減らす手技で、スムーズな動かしやすさを取り戻します。{cta}",
                "bg_query": "physical therapist stretching arms therapy",
                "bg_queries": [
                    "physical therapist stretching arms therapy",
                    "shoulder rehabilitation manual exercise",
                    "arm mobility therapy physical clinic"
                ]
            }
        ]
    },

    # =========================================================================
    # カテゴリー6: レッドコード (全3本)
    # =========================================================================
    {
        "theme_id": "theme_6_1",
        "category": "レッドコード",
        "title": "痛くない転ばない赤いロープ運動 #Shorts",
        "variations": [
            {
                "pattern_id": "PATTERN_SURPRISE",
                "hook_type": "SURPRISE",
                "structure_type": "HOOK → EXPLANATION → CTA",
                "angle": "両手でロープを握るから転ぶ心配ゼロの安心健康運動",
                "narration_template": "痛くない、転ばない、無理がない。両手で赤いロープを握って体を預けるから、膝や腰に負担なく運動できます。{cta}",
                "bg_query": "sling suspension therapy rehabilitation exercise",
                "bg_queries": [
                    "sling suspension therapy rehabilitation exercise",
                    "redcord sling therapy patient exercise",
                    "suspension sling training physiotherapy"
                ]
            },
            {
                "pattern_id": "PATTERN_COMMON_MISTAKE",
                "hook_type": "COMMON_MISTAKE",
                "structure_type": "COMMON_MISTAKE → CORRECTION → CTA",
                "angle": "膝や腰の痛みで運動を諦めていた方への安心免荷運動",
                "narration_template": "膝や腰が痛くて運動を諦めていませんか？赤いロープが体重を支えてくれるため、痛みなく安全に体を動かせます。{cta}",
                "bg_query": "redcord sling therapy patient exercise",
                "bg_queries": [
                    "redcord sling therapy patient exercise",
                    "sling therapy gentle patient movement",
                    "suspension therapy safe senior training"
                ]
            },
            {
                "pattern_id": "PATTERN_BENEFIT",
                "hook_type": "BENEFIT",
                "structure_type": "BENEFIT → METHOD → CTA",
                "angle": "両手で体を預けて関節負担を減らすノルウェー発祥機器",
                "narration_template": "ノルウェー生まれのレッドコード。頑丈なロープを両手で握るだけで、関節への負担を最小限に運動できます。{cta}",
                "bg_query": "suspension sling training physiotherapy",
                "bg_queries": [
                    "suspension sling training physiotherapy",
                    "core training sling suspension clinic",
                    "rehabilitation suspension ropes therapy"
                ]
            }
        ]
    },
    {
        "theme_id": "theme_6_2",
        "category": "レッドコード",
        "title": "握るだけで体幹を鍛える新習慣 #Shorts",
        "variations": [
            {
                "pattern_id": "PATTERN_SCENE",
                "hook_type": "SCENE",
                "structure_type": "SCENE → INSIGHT → CTA",
                "angle": "もたれかかるだけで肩甲骨ほぐしから安全スクワットまで",
                "narration_template": "赤いロープを握ってもたれかかるだけ。肩甲骨のストレッチから膝を痛めないスクワットまで、安全に行えます。{cta}",
                "bg_query": "core balance rehabilitation training",
                "bg_queries": [
                    "core balance rehabilitation training",
                    "balance exercise physical therapy senior",
                    "rehabilitation sling training indoor"
                ]
            },
            {
                "pattern_id": "PATTERN_QUESTION",
                "hook_type": "QUESTION",
                "structure_type": "QUESTION → REASON → CTA",
                "angle": "ハードな運動が不安な方でも自然に働く体幹バランス",
                "narration_template": "体幹を鍛えたいけれどハードな運動は不安？ロープに体重を預けて少し傾くだけで、深層部の筋肉が自然と働きます。{cta}",
                "bg_query": "balance exercise physical therapy senior",
                "bg_queries": [
                    "balance exercise physical therapy senior",
                    "senior balance training physical therapist",
                    "stability balance exercise clinic senior"
                ]
            },
            {
                "pattern_id": "PATTERN_BENEFIT",
                "hook_type": "BENEFIT",
                "structure_type": "BENEFIT → METHOD → CTA",
                "angle": "体重をロープに預けて深層筋肉にピンポイントで効く",
                "narration_template": "ピンポイントで効くのに体に優しい。体重をロープに預けることで、普段使えないインナーマッスルを刺激します。{cta}",
                "bg_query": "rehabilitation sling training indoor",
                "bg_queries": [
                    "rehabilitation sling training indoor",
                    "safe core strengthening therapy",
                    "indoor gait and balance rehab"
                ]
            }
        ]
    },
    {
        "theme_id": "theme_6_3",
        "category": "レッドコード",
        "title": "ふらつき予防にノルウェー発の運動 #Shorts",
        "variations": [
            {
                "pattern_id": "PATTERN_BENEFIT",
                "hook_type": "BENEFIT",
                "structure_type": "BENEFIT → METHOD → CTA",
                "angle": "足腰の衰えや転倒の不安を解消する基本のロープ運動",
                "narration_template": "足腰の衰えや転倒が不安な方へ。天井から吊るされた頑丈なロープを両手で掴むため、ふらつかず安心して動けます。{cta}",
                "bg_query": "stretching ropes relaxation exercise",
                "bg_queries": [
                    "stretching ropes relaxation exercise",
                    "sling exercise relaxation physiotherapy",
                    "suspension therapy physical therapy clinic"
                ]
            },
            {
                "pattern_id": "PATTERN_QUESTION",
                "hook_type": "QUESTION",
                "structure_type": "QUESTION → REASON → CTA",
                "angle": "体が硬く運動が苦手でも自分の力に合わせられる健康法",
                "narration_template": "体が硬い、運動が苦手と諦めていませんか？レッドコードなら、ご自身の体力に合わせた無理のない運動が可能です。{cta}",
                "bg_query": "sling exercise relaxation physiotherapy",
                "bg_queries": [
                    "sling exercise relaxation physiotherapy",
                    "patient relaxing in suspension sling",
                    "gentle decompression stretching physical therapy"
                ]
            },
            {
                "pattern_id": "PATTERN_SURPRISE",
                "hook_type": "SURPRISE",
                "structure_type": "HOOK → EXPLANATION → CTA",
                "angle": "赤いロープに身を預ける心地よさと体幹安定リセット",
                "narration_template": "赤いロープに体を預ける心地よさ。余分な力を抜きながら、ぶれない安定した立ち姿勢を自然に取り戻します。{cta}",
                "bg_query": "suspension therapy physical therapy clinic",
                "bg_queries": [
                    "suspension therapy physical therapy clinic",
                    "floating sensation physical therapy sling",
                    "relaxation mobility training clinic"
                ]
            }
        ]
    },

    # =========================================================================
    # カテゴリー7: 小規模多機能型居宅介護 (全3本)
    # =========================================================================
    {
        "theme_id": "theme_7_1",
        "category": "小規模多機能",
        "title": "通い泊まり訪問をひとつの窓口で #Shorts",
        "variations": [
            {
                "pattern_id": "PATTERN_SURPRISE",
                "hook_type": "SURPRISE",
                "structure_type": "HOOK → EXPLANATION → CTA",
                "angle": "通い・泊まり・訪問を顔なじみスタッフが一体提供する安心",
                "narration_template": "通い、泊まり、訪問の3つを同じ施設で。いつも顔なじみのスタッフが対応するから、環境が変わるストレスもありません。{cta}",
                "bg_query": "home caregiver assisting senior smiling",
                "bg_queries": [
                    "home caregiver assisting senior smiling",
                    "nurse holding senior hands caring",
                    "caregiver visiting senior home"
                ]
            },
            {
                "pattern_id": "PATTERN_QUESTION",
                "hook_type": "QUESTION",
                "structure_type": "QUESTION → REASON → CTA",
                "angle": "サービスごとに人が変わる認知症シニアの混乱を防ぐ",
                "narration_template": "介護サービスごとに人が変わって混乱していませんか？小規模多機能なら、いつものスタッフが寄り添い安心を支えます。{cta}",
                "bg_query": "nurse holding senior hands caring",
                "bg_queries": [
                    "nurse holding senior hands caring",
                    "comforting nurse and senior patient",
                    "elderly care trust relationship"
                ]
            },
            {
                "pattern_id": "PATTERN_BENEFIT",
                "hook_type": "BENEFIT",
                "structure_type": "BENEFIT → METHOD → CTA",
                "angle": "基本料金が月額定額制で費用が見通しやすい安心の仕組み",
                "narration_template": "基本料金は月額定額制。利用回数が増えても介護費用の見通しが立ちやすく、ケアマネジャーとも常に連携できます。{cta}",
                "bg_query": "caregiver visiting senior home",
                "bg_queries": [
                    "caregiver visiting senior home",
                    "home healthcare visit elderly patient",
                    "community home nursing care"
                ]
            }
        ]
    },
    {
        "theme_id": "theme_7_2",
        "category": "小規模多機能",
        "title": "急な宿泊にも柔軟に応える在宅介護 #Shorts",
        "variations": [
            {
                "pattern_id": "PATTERN_SCENE",
                "hook_type": "SCENE",
                "structure_type": "SCENE → INSIGHT → CTA",
                "angle": "家族の急な用事や体調変化に合わせて柔軟にサービス切替",
                "narration_template": "急な仕事や家族の体調不良でも大丈夫。通いの日でも訪問や泊まりへ柔軟に切り替え、在宅介護の負担を大きく減らします。{cta}",
                "bg_query": "elderly couple happy at home",
                "bg_queries": [
                    "elderly couple happy at home",
                    "senior sitting living room tea peaceful",
                    "senior woman smiling comfortable home"
                ]
            },
            {
                "pattern_id": "PATTERN_QUESTION",
                "hook_type": "QUESTION",
                "structure_type": "QUESTION → REASON → CTA",
                "angle": "在宅介護の限界を感じた時に頼れる臨機応変なサポート",
                "narration_template": "在宅介護に限界を感じていませんか？「少し様子を見てほしい」「急に泊まりたい」という突発的なご要望にもすぐ対応します。{cta}",
                "bg_query": "senior sitting living room tea peaceful",
                "bg_queries": [
                    "senior sitting living room tea peaceful",
                    "elderly person relaxing home living room",
                    "peaceful home living senior"
                ]
            },
            {
                "pattern_id": "PATTERN_BENEFIT",
                "hook_type": "BENEFIT",
                "structure_type": "BENEFIT → METHOD → CTA",
                "angle": "住み慣れた自宅でずっと暮らし続けられる継続支援体制",
                "narration_template": "住み慣れた自宅でずっと暮らしたい。ご本人の希望とご家族の生活を、24時間365日柔軟なサポートで支え続けます。{cta}",
                "bg_query": "senior woman smiling comfortable home",
                "bg_queries": [
                    "senior woman smiling comfortable home",
                    "warm home care elderly support",
                    "happy senior living independently"
                ]
            }
        ]
    },
    {
        "theme_id": "theme_7_3",
        "category": "小規模多機能",
        "title": "クリニック母体だから医療処置も安心 #Shorts",
        "variations": [
            {
                "pattern_id": "PATTERN_SURPRISE",
                "hook_type": "SURPRISE",
                "structure_type": "HOOK → EXPLANATION → CTA",
                "angle": "クリニック直結だから医療処置が必要な方も在宅生活継続",
                "narration_template": "医療機関が運営母体だから安心。インスリンや胃ろうなどの医療処置が必要な方でも、住み慣れた自宅での生活を継続できます。{cta}",
                "bg_query": "nurse caring for elderly comforting",
                "bg_queries": [
                    "nurse caring for elderly comforting",
                    "elderly person with nurse laughing",
                    "senior care home comfortable environment"
                ]
            },
            {
                "pattern_id": "PATTERN_COMMON_MISTAKE",
                "hook_type": "COMMON_MISTAKE",
                "structure_type": "COMMON_MISTAKE → CORRECTION → CTA",
                "angle": "日頃の体調変化の早期発見と母体クリニックへの迅速連携",
                "narration_template": "体調が急に変わったらと不安ではありませんか？日頃のわずかな変化を察知し、母体クリニックへ迅速に連携・受診できます。{cta}",
                "bg_query": "elderly person with nurse laughing",
                "bg_queries": [
                    "elderly person with nurse laughing",
                    "caring nurse laughing with senior resident",
                    "trusting relationship nurse and elderly"
                ]
            },
            {
                "pattern_id": "PATTERN_BENEFIT",
                "hook_type": "BENEFIT",
                "structure_type": "BENEFIT → METHOD → CTA",
                "angle": "退院直後から通い泊まり訪問を組み合わせて多職種で連携",
                "narration_template": "病院の退院直後からスムーズに在宅へ。医師や看護師、ケアマネジャーが一体となり、チームで安心の生活を支えます。{cta}",
                "bg_query": "senior care home comfortable environment",
                "bg_queries": [
                    "senior care home comfortable environment",
                    "comfortable nursing home atmosphere",
                    "gentle caregiver supporting elderly person"
                ]
            }
        ]
    }
,
    # =========================================================================
    # カテゴリー8: 外来診療 (全3本)
    # =========================================================================
    {
        "theme_id": "theme_8_1",
        "category": "外来診療",
        "title": "何科に行くか迷ったらまず当院へ #Shorts",
        "variations": [
            {
                "pattern_id": "PATTERN_SURPRISE",
                "hook_type": "SURPRISE",
                "structure_type": "HOOK → EXPLANATION → CTA",
                "angle": "専門内科に絞らないからこそ身体のことを何でも相談できる",
                "narration_template": "何科に行けばいいか迷っていませんか？特定の専門に絞らないからこそ、身体のお悩みを何でも相談できる場所があります。{cta}",
                "bg_query": "doctor consulting patient clinic",
                "bg_queries": [
                    "doctor consulting patient clinic",
                    "friendly doctor talking with senior patient",
                    "healthcare clinic reception consultation"
                ]
            },
            {
                "pattern_id": "PATTERN_QUESTION",
                "hook_type": "QUESTION",
                "structure_type": "QUESTION → REASON → CTA",
                "angle": "病院に行くべきか迷う初期症状も気軽に相談できる窓口",
                "narration_template": "「こんなことで病院に行っていいのかな」と悩んでいませんか？些細な体調不良も、地域のホームドクターへまずご相談ください。{cta}",
                "bg_query": "friendly doctor talking with senior patient",
                "bg_queries": [
                    "friendly doctor talking with senior patient",
                    "caring doctor listening elderly patient",
                    "clinic medical consultation senior"
                ]
            },
            {
                "pattern_id": "PATTERN_BENEFIT",
                "hook_type": "BENEFIT",
                "structure_type": "BENEFIT → METHOD → CTA",
                "angle": "まず受け止め必要な専門医療機関や高次病院へ適切につなぐ",
                "narration_template": "まずは気軽に相談できる場所へ。当院で幅広く診療しながら、より専門的な治療が必要な際も高次病院へ適切におつなぎします。{cta}",
                "bg_query": "healthcare clinic reception consultation",
                "bg_queries": [
                    "healthcare clinic reception consultation",
                    "patient talking with healthcare professional",
                    "modern hospital clinic reception"
                ]
            }
        ]
    },
    {
        "theme_id": "theme_8_2",
        "category": "外来診療",
        "title": "負担の少ないエコーや各種迅速検査 #Shorts",
        "variations": [
            {
                "pattern_id": "PATTERN_SCENE",
                "hook_type": "SCENE",
                "structure_type": "SCENE → INSIGHT → CTA",
                "angle": "身体に優しいエコー検査で心臓や血管など各部位を詳しく確認",
                "narration_template": "身体への負担が少ないエコー検査。心臓や血管、腹部など、気になる症状に合わせて苦痛なく詳しい状態を確認できます。{cta}",
                "bg_query": "ultrasound medical examination clinic",
                "bg_queries": [
                    "ultrasound medical examination clinic",
                    "medical ultrasound scan examination",
                    "doctor performing diagnostic test"
                ]
            },
            {
                "pattern_id": "PATTERN_QUESTION",
                "hook_type": "QUESTION",
                "structure_type": "QUESTION → REASON → CTA",
                "angle": "血糖値や血圧が心配な方のための当日結果と早期生活習慣病対策",
                "narration_template": "血糖値や血圧の数値が気になっていませんか？当日に結果がわかる血液検査や各種健診で、病気の早期発見をサポートします。{cta}",
                "bg_query": "medical checkup health consultation doctor",
                "bg_queries": [
                    "medical checkup health consultation doctor",
                    "blood pressure test senior clinic",
                    "health checkup lifestyle disease clinic"
                ]
            },
            {
                "pattern_id": "PATTERN_BENEFIT",
                "hook_type": "BENEFIT",
                "structure_type": "BENEFIT → METHOD → CTA",
                "angle": "病気になってから治すのではなく健診や予防接種で健康を守る",
                "narration_template": "病気になってから治すのではなく、未然に防ぐ。特定健診や各種予防接種で、地域の皆さまの長く元気な暮らしを守ります。{cta}",
                "bg_query": "senior patient health examination",
                "bg_queries": [
                    "senior patient health examination",
                    "preventive medicine checkup senior",
                    "healthy elderly patient medical checkup"
                ]
            }
        ]
    },
    {
        "theme_id": "theme_8_3",
        "category": "外来診療",
        "title": "専門医連携と介護まで支える医療 #Shorts",
        "variations": [
            {
                "pattern_id": "PATTERN_SURPRISE",
                "hook_type": "SURPRISE",
                "structure_type": "HOOK → EXPLANATION → CTA",
                "angle": "金曜専門医による関節ハイドロリリースなど専門治療に対応",
                "narration_template": "長引く関節の痛みにお悩みの方へ。大学病院の専門医による関節のハイドロリリースなど、専門的な治療にも対応しています。{cta}",
                "bg_query": "doctor and specialist healthcare team",
                "bg_queries": [
                    "doctor and specialist healthcare team",
                    "orthopedic doctor consultation clinic",
                    "joint pain medical consultation specialist"
                ]
            },
            {
                "pattern_id": "PATTERN_BENEFIT",
                "hook_type": "BENEFIT",
                "structure_type": "BENEFIT → METHOD → CTA",
                "angle": "医療だけでなくリハビリから介護サービスまで法人全体で支援",
                "narration_template": "医療だけでなく介護までトータルサポート。外来リハビリや通所サービスと連携し、退院後の生活や在宅生活を支えます。{cta}",
                "bg_query": "physical therapy and healthcare clinic consultation",
                "bg_queries": [
                    "physical therapy and healthcare clinic consultation",
                    "comprehensive healthcare and nursing care clinic",
                    "rehabilitation team clinic consultation"
                ]
            },
            {
                "pattern_id": "PATTERN_COMMON_MISTAKE",
                "hook_type": "COMMON_MISTAKE",
                "structure_type": "COMMON_MISTAKE → CORRECTION → CTA",
                "angle": "土曜の専門外来と地域高次病院との連携による安心の医療体制",
                "narration_template": "土曜日の専門外来や地域病院との連携体制。普段の診察から高度な専門医療まで、安心のネットワークでお応えします。{cta}",
                "bg_query": "caring doctor patient rehabilitation",
                "bg_queries": [
                    "caring doctor patient rehabilitation",
                    "medical network doctor referral clinic",
                    "trusted local healthcare doctor"
                ]
            }
        ]
    }
]

# カテゴリー巡回（Round-Robin）順への自動再編成
# 同じカテゴリーを連続させず、1つずつカテゴリーをローテーションさせる
def _interleave_themes_by_category(themes_list):
    categories = []
    by_cat = {}
    for t in themes_list:
        c = t.get('category', '')
        if c not in by_cat:
            categories.append(c)
            by_cat[c] = []
        by_cat[c].append(t)
    
    interleaved = []
    max_len = max(len(v) for v in by_cat.values()) if by_cat else 0
    for i in range(max_len):
        for c in categories:
            if i < len(by_cat[c]):
                interleaved.append(by_cat[c][i])
    return interleaved

THEMES = _interleave_themes_by_category(THEMES)

# デフォルト設定の補完
for _t in THEMES:
    if "variations" in _t and len(_t["variations"]) > 0:
        _v0 = _t["variations"][0]
        if "narration" not in _t:
            _t["narration"] = _v0["narration_template"].format(cta=CTA_VARIATIONS[0])
        if "bg_query" not in _t:
            _t["bg_query"] = _v0["bg_query"]
        if "pattern_id" not in _t:
            _t["pattern_id"] = _v0.get("pattern_id", "PATTERN_SURPRISE")
        if "hook_type" not in _t:
            _t["hook_type"] = _v0.get("hook_type", "SURPRISE")
        if "structure_type" not in _t:
            _t["structure_type"] = _v0.get("structure_type", "HOOK → EXPLANATION → CTA")
        if "angle" not in _t:
            _t["angle"] = _v0.get("angle", "")

DEFAULT_THEME = THEMES[0]

def apply_variation_to_theme(theme, pattern_index=None, cta_index=None):
    """
    テーマ辞書に指定またはランダムなバリエーションとCTAを適用して返す
    """
    t_copy = dict(theme)
    variations = t_copy.get('variations', [])
    if not variations:
        return t_copy

    if pattern_index is not None and 0 <= pattern_index < len(variations):
        v = variations[pattern_index]
    else:
        v = random.choice(variations)

    if cta_index is not None and 0 <= cta_index < len(CTA_VARIATIONS):
        cta = CTA_VARIATIONS[cta_index]
    else:
        cta = random.choice(CTA_VARIATIONS)

    template = v.get('narration_template', v.get('narration', ''))
    if '{cta}' in template:
        t_copy['narration'] = template.format(cta=cta)
    else:
        t_copy['narration'] = template

    # 背景クエリの選定（字幕内容に最も合致する第一優先クエリを先頭とし、優先順位リストを保持）
    bg_candidates = v.get('bg_queries', [v.get('bg_query', 'medical consultation doctor clinic')])
    t_copy['bg_query'] = bg_candidates[0] if bg_candidates else v.get('bg_query', 'medical clinic')
    t_copy['bg_queries'] = bg_candidates

    t_copy['pattern_id'] = v.get('pattern_id', 'PATTERN_SURPRISE')
    t_copy['hook_type'] = v.get('hook_type', 'SURPRISE')
    t_copy['structure_type'] = v.get('structure_type', 'HOOK → EXPLANATION → CTA')
    t_copy['angle'] = v.get('angle', '')
    t_copy['cta'] = cta
    return t_copy

def get_theme_by_id(theme_id, pattern_index=None, cta_index=None):
    for t in THEMES:
        if t["theme_id"] == theme_id:
            return apply_variation_to_theme(t, pattern_index, cta_index)
    return apply_variation_to_theme(DEFAULT_THEME, pattern_index, cta_index)

def get_all_themes():
    return [apply_variation_to_theme(t) for t in THEMES]

# ==============================================================================
# 本番運用用：日次順次ローテーション選択
# ==============================================================================
def select_next_theme(state_file=STATE_FILE_PATH):
    env_theme_id = os.environ.get('THEME_ID', '').strip()
    if env_theme_id:
        for t in THEMES:
            if t['theme_id'] == env_theme_id:
                print(f"[THEME] Selected theme from environment THEME_ID: {env_theme_id}")
                return apply_variation_to_theme(t)
        print(f"[THEME WARNING] THEME_ID '{env_theme_id}' not found in THEMES. Falling back to rotation.")

    if not os.path.exists(state_file):
        return apply_variation_to_theme(THEMES[0])

    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            last_theme_id = data.get('last_theme_id')
            last_category = data.get('category')
            last_index = -1
            if last_theme_id:
                for idx, t in enumerate(THEMES):
                    if t.get('theme_id') == last_theme_id:
                        last_index = idx
                        break
            if last_index == -1:
                last_index = data.get('last_theme_index', data.get('last_index', -1))

            next_index = (last_index + 1) % len(THEMES)
            selected = THEMES[next_index]

            # 安全ガード: 同じカテゴリーが2回以上連続して投稿されることを確実に防止
            if len(THEMES) > 1 and last_category and selected.get('category') == last_category:
                for offset in range(1, len(THEMES)):
                    candidate_idx = (next_index + offset) % len(THEMES)
                    if THEMES[candidate_idx].get('category') != last_category:
                        next_index = candidate_idx
                        selected = THEMES[next_index]
                        break

            print(f"[PRODUCTION MODE] Theme rotation: index {next_index}/{len(THEMES)-1} ({selected['theme_id']} - {selected['category']})")
            return apply_variation_to_theme(selected)
    except Exception as e:
        print(f"[THEME ERROR] Failed to read theme state: {e}. Falling back to default theme.")
        return apply_variation_to_theme(THEMES[0])

def commit_theme_state(theme, state_file=STATE_FILE_PATH):
    theme_id = theme.get('theme_id')
    theme_index = -1
    for i, t in enumerate(THEMES):
        if t['theme_id'] == theme_id:
            theme_index = i
            break

    if theme_index == -1:
        print(f"[THEME WARNING] Cannot commit unknown theme_id: {theme_id}")
        return False

    os.makedirs(os.path.dirname(state_file), exist_ok=True)
    state_data = {
        'last_theme_index': theme_index,
        'last_index': theme_index,
        'last_theme_id': theme_id,
        'category': theme.get('category', ''),
        'title': theme.get('title', ''),
        'pattern_id': theme.get('pattern_id', 'PATTERN_A'),
        'hook_type': theme.get('hook_type', 'SURPRISE'),
        'updated_at': os.environ.get('GITHUB_RUN_ID', 'local_run')
    }

    try:
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, ensure_ascii=False, indent=2)
        print(f"[THEME STATE COMMITTED] Successfully updated state to theme_index={theme_index} ({theme_id})")
        return True
    except Exception as e:
        print(f"[THEME ERROR] Failed to write theme state: {e}")
        return False

# ==============================================================================
# テスト専用：多次元アンチリピート・シャッフルプール選択エンジン
# ==============================================================================
def select_random_test_theme(state_file=TEST_STATE_FILE_PATH):
    """
    全21テーマをランダムシャッフルし、全テーマを使い切るまで重複なく1つずつ取り出す。
    さらに、直近の履歴から「同じHOOK TYPE」「同じSTRUCTURE」「同じBG QUERY」が連続しないように
    多次元アンチリピート制御を行ってバリエーションを選定する。
    """
    all_ids = [t['theme_id'] for t in THEMES]
    remaining_ids = []
    cycle = 1
    last_history = {}

    if os.path.exists(state_file):
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
                remaining_ids = state_data.get('remaining_theme_ids', [])
                cycle = state_data.get('cycle_count', 1)
                last_history = state_data.get('last_history', {})
        except Exception:
            remaining_ids = []

    if not remaining_ids:
        remaining_ids = list(all_ids)
        random.shuffle(remaining_ids)
        if os.path.exists(state_file):
            cycle += 1

    selected_id = remaining_ids.pop(0)
    raw_theme = None
    for t in THEMES:
        if t['theme_id'] == selected_id:
            raw_theme = t
            break
    if raw_theme is None:
        raw_theme = DEFAULT_THEME

    # 多次元アンチリピートによるバリエーション選定
    variations = raw_theme.get('variations', [])
    last_hook = last_history.get('hook_type')
    last_structure = last_history.get('structure_type')
    last_bg_query = last_history.get('bg_query')
    last_cta = last_history.get('cta')

    # 直前と異なる hook_type, structure_type を優先探索
    candidate_indices = []
    for idx, v in enumerate(variations):
        score = 0
        if v.get('hook_type') != last_hook:
            score += 2
        if v.get('structure_type') != last_structure:
            score += 2
        if v.get('bg_query') != last_bg_query:
            score += 1
        candidate_indices.append((score, idx))

    candidate_indices.sort(key=lambda x: x[0], reverse=True)
    best_pattern_index = candidate_indices[0][1]

    # 直前と異なる CTA を選定
    available_ctas = [i for i, c in enumerate(CTA_VARIATIONS) if c != last_cta]
    best_cta_index = random.choice(available_ctas) if available_ctas else 0

    selected_theme = apply_variation_to_theme(raw_theme, best_pattern_index, best_cta_index)

    # 履歴と状態を保存
    os.makedirs(os.path.dirname(state_file), exist_ok=True)
    try:
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump({
                'cycle_count': cycle,
                'last_selected_id': selected_id,
                'last_history': {
                    'theme_id': selected_id,
                    'hook_type': selected_theme.get('hook_type'),
                    'structure_type': selected_theme.get('structure_type'),
                    'bg_query': selected_theme.get('bg_query'),
                    'cta': selected_theme.get('cta')
                },
                'remaining_theme_ids': remaining_ids,
                'remaining_count': len(remaining_ids),
                'total_themes': len(THEMES)
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[TEST THEME ERROR] Failed to save test theme state: {e}")

    print("[TEST MODE]")
    print(f"theme selection mode: SHUFFLE_POOL (Cycle {cycle})")
    print(f"theme_id: {selected_theme['theme_id']}")
    print(f"category: {selected_theme['category']}")
    print(f"title: {selected_theme['title']}")
    print(f"hook_type: {selected_theme.get('hook_type')}")
    print(f"structure: {selected_theme.get('structure_type')}")
    print(f"angle: {selected_theme.get('angle')}")
    print(f"bg_query: {selected_theme.get('bg_query')}")
    print(f"cta: {selected_theme.get('cta')}")
    print(f"remaining in pool: {len(remaining_ids)}/{len(THEMES)}")

    return selected_theme
