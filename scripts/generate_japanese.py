#!/usr/bin/env python3
"""
日本語訳＋ルビ自動生成スクリプト
- ソース: data/kjv/*.json（KJV全66冊）
- モデル: Claude Haiku（安価・高速）
- 出力: data/japanese/*.json
- 再開可能: 途中で止めても続きから再開できる

使い方:
  1. pip install anthropic
  2. export ANTHROPIC_API_KEY="your_key_here"
  3. python3 generate_japanese.py
"""

import json
import os
import time
import glob
from pathlib import Path

import anthropic

# ── 設定 ──────────────────────────────────────────
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = "claude-haiku-4-5-20251001"
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
INPUT_DIR = PROJECT_DIR / "data" / "kjv"
OUTPUT_DIR = PROJECT_DIR / "data" / "japanese"
BATCH_SIZE = 25       # 1回のAPIコールで処理する節数
DELAY = 2.0           # APIコール間の待機秒数（レート制限対策）
# ─────────────────────────────────────────────────

SYSTEM_PROMPT = """あなたは聖書の翻訳者です。
KJV（欽定訳聖書）の英語テキストを自然な現代日本語に翻訳してください。

出力形式（JSONのみ、他の文章は一切不要）:
[
  {"v": 1, "t": "神は天と地を創られた。"},
  {"v": 2, "t": "..."}
]

ルール:
- 固有名詞（イエス・ダビデ等）はカタカナで
- 自然で読みやすい現代語訳
- JSONのみ出力（```json等のマークダウン不要）
"""

def translate_batch(client, verses: list, book_name: str, chapter: int) -> list:
    """複数節をまとめて翻訳"""
    verses_text = "\n".join([f"{v['v']}. {v['t']}" for v in verses])
    prompt = f"{book_name} 第{chapter}章\n\n{verses_text}"

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=8192,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.content[0].text.strip()

        # マークダウンのコードブロックを除去
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()

        result = json.loads(text)
        return result

    except json.JSONDecodeError as e:
        # バッチを半分に分けてリトライ
        if len(verses) > 1:
            print(f"    JSON切れ → バッチ分割してリトライ...")
            mid = len(verses) // 2
            left = translate_batch(client, verses[:mid], book_name, chapter)
            right = translate_batch(client, verses[mid:], book_name, chapter)
            if left and right:
                return left + right
        print(f"    JSON parse error: {e}")
        return None
    except Exception as e:
        err = str(e)
        if "429" in err or "rate_limit" in err.lower() or "overloaded" in err.lower():
            print(f"    レート制限 - 60秒待機中...")
            time.sleep(60)
            return translate_batch(client, verses, book_name, chapter)
        if "529" in err or "503" in err or "overload" in err.lower():
            print(f"    サーバー過負荷 - 30秒待機中...")
            time.sleep(30)
            return translate_batch(client, verses, book_name, chapter)
        print(f"    API error: {e}")
        return None

def process_chapter(client, chapter_data: dict, book_name_ja: str, chapter_num: int) -> list:
    """1章分を処理（バッチ分割）"""
    kjv_verses = chapter_data.get("kjv", [])
    if not kjv_verses:
        return []

    all_japanese = []

    # BATCH_SIZE節ずつ処理
    for i in range(0, len(kjv_verses), BATCH_SIZE):
        batch = kjv_verses[i:i + BATCH_SIZE]
        print(f"      節 {batch[0]['v']}〜{batch[-1]['v']}...", end=" ", flush=True)

        result = translate_batch(client, batch, book_name_ja, chapter_num)

        if result:
            all_japanese.extend(result)
            print("✓")
        else:
            # 失敗した場合はプレースホルダーを入れる
            for v in batch:
                all_japanese.append({"v": v["v"], "t": f"[翻訳エラー: {v['t'][:50]}...]"})
            print("✗ (プレースホルダー)")

        time.sleep(DELAY)

    return all_japanese

def process_book(client, book_path: Path, output_dir: Path) -> bool:
    """1冊分を処理"""
    with open(book_path, encoding="utf-8") as f:
        book_data = json.load(f)

    book_id = book_data["id"]
    book_name_ja = book_data.get("nameJa", book_data["nameEn"])
    chapters = book_data.get("chapters", {})

    output_path = output_dir / f"{book_id}.json"

    # 既存の進捗を読み込む（再開用）
    existing = {}
    if output_path.exists():
        with open(output_path, encoding="utf-8") as f:
            existing = json.load(f)

    result = dict(existing)  # 既存データをコピー

    for ch_num_str, ch_data in chapters.items():
        ch_num = int(ch_num_str)

        # 既に翻訳済み かつ エラーなし ならスキップ
        if ch_num_str in result and result[ch_num_str].get("japanese"):
            verses = result[ch_num_str]["japanese"]
            has_error = any("翻訳エラー" in v.get("t", "") for v in verses)
            if not has_error:
                print(f"    第{ch_num}章 スキップ（翻訳済み）")
                continue
            print(f"    第{ch_num}章 再翻訳（エラーあり）...")

        print(f"    第{ch_num}章 翻訳中...")
        japanese_verses = process_chapter(client, ch_data, book_name_ja, ch_num)

        if ch_num_str not in result:
            result[ch_num_str] = {}
        result[ch_num_str]["japanese"] = japanese_verses

        # 章ごとに保存（途中で止まっても安全）
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

    return True

def main():
    if not API_KEY:
        print("エラー: ANTHROPIC_API_KEY が設定されていません")
        print("export ANTHROPIC_API_KEY='your_key_here'")
        return

    if not INPUT_DIR.exists():
        print(f"エラー: {INPUT_DIR} が見つかりません")
        print("先に fetch_kjv.py を実行してください")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    client = anthropic.Anthropic(api_key=API_KEY)

    book_files = sorted(INPUT_DIR.glob("*.json"))
    book_files = [f for f in book_files if f.name != "index.json"]

    print(f"対象: {len(book_files)}冊")
    print(f"モデル: {MODEL}")
    print(f"バッチサイズ: {BATCH_SIZE}節/回")
    print("=" * 50)

    for i, book_path in enumerate(book_files, 1):
        with open(book_path, encoding="utf-8") as f:
            meta = json.load(f)
        book_name = meta.get("nameJa", meta["nameEn"])
        ch_count = len(meta.get("chapters", {}))

        print(f"\n[{i:2d}/{len(book_files)}] {book_name} ({ch_count}章)")
        process_book(client, book_path, OUTPUT_DIR)

    print("\n" + "=" * 50)
    print("完了！")
    print(f"出力先: {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
