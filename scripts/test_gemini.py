#!/usr/bin/env python3
"""
テスト用スクリプト - ヨハネ3:16〜18の3節だけ翻訳して動作確認
使い方:
  export GEMINI_API_KEY="your_key_here"
  python3 test_gemini.py
"""

import os
import json
from google import genai
from google.genai import types

API_KEY = os.environ.get("GEMINI_API_KEY", "")

SYSTEM_PROMPT = """あなたは聖書の翻訳者です。
KJV（欽定訳聖書）の英語テキストを自然な現代日本語に翻訳し、
すべての漢字にHTMLのrubyタグでフリガナを付けてください。

出力形式（JSONのみ、他の文章は一切不要）:
[
  {"v": 1, "t": "<ruby>神<rt>かみ</rt></ruby>は..."}
]

ルール:
- rubyタグは <ruby>漢字<rt>よみ</rt></ruby> の形式
- ひらがな・カタカナにはrubyタグ不要
- 固有名詞（イエス・ダビデ等）はカタカナで
- 自然で読みやすい現代語訳
- JSONのみ出力（```json等のマークダウン不要）
"""

TEST_VERSES = [
    {"v": 16, "t": "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life."},
    {"v": 17, "t": "For God sent not his Son into the world to condemn the world; but that the world through him might be saved."},
    {"v": 18, "t": "He that believeth on him is not condemned: but he that believeth not is condemned already, because he hath not believed in the name of the only begotten Son of God."},
]

def main():
    if not API_KEY:
        print("エラー: GEMINI_API_KEY が設定されていません")
        print("export GEMINI_API_KEY='your_key_here'")
        return

    client = genai.Client(api_key=API_KEY)

    verses_text = "\n".join([f"{v['v']}. {v['t']}" for v in TEST_VERSES])
    prompt = f"ヨハネ 第3章\n\n{verses_text}"

    print("テスト送信中...")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.3,
        )
    )
    text = response.text.strip()

    print("\n--- APIレスポンス ---")
    print(text)

    # JSON解析テスト
    try:
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        result = json.loads(text.strip())
        print("\n--- 解析結果 ---")
        for v in result:
            print(f"節{v['v']}: {v['t']}")
        print("\n✓ テスト成功！generate_japanese.py を実行できます")
    except Exception as e:
        print(f"\n✗ JSON解析エラー: {e}")

if __name__ == "__main__":
    main()
