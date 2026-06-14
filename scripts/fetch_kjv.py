#!/usr/bin/env python3
"""
KJV全66巻データ取得スクリプト
ソース: https://github.com/aruljohn/Bible-kjv (Public Domain)
出力: data/kjv/ に各書籍のJSONファイル
"""

import json
import time
import os
import urllib.request

BASE_URL = "https://raw.githubusercontent.com/aruljohn/Bible-kjv/master"

BOOKS = [
    # 旧約 (39冊)
    ("Genesis",       "創世記"),
    ("Exodus",        "出エジプト記"),
    ("Leviticus",     "レビ記"),
    ("Numbers",       "民数記"),
    ("Deuteronomy",   "申命記"),
    ("Joshua",        "ヨシュア記"),
    ("Judges",        "士師記"),
    ("Ruth",          "ルツ記"),
    ("1Samuel",       "サムエル記上"),
    ("2Samuel",       "サムエル記下"),
    ("1Kings",        "列王記上"),
    ("2Kings",        "列王記下"),
    ("1Chronicles",   "歴代誌上"),
    ("2Chronicles",   "歴代誌下"),
    ("Ezra",          "エズラ記"),
    ("Nehemiah",      "ネヘミヤ記"),
    ("Esther",        "エステル記"),
    ("Job",           "ヨブ記"),
    ("Psalms",        "詩篇"),
    ("Proverbs",      "箴言"),
    ("Ecclesiastes",  "伝道の書"),
    ("SongofSolomon", "雅歌"),
    ("Isaiah",        "イザヤ書"),
    ("Jeremiah",      "エレミヤ書"),
    ("Lamentations",  "哀歌"),
    ("Ezekiel",       "エゼキエル書"),
    ("Daniel",        "ダニエル書"),
    ("Hosea",         "ホセア書"),
    ("Joel",          "ヨエル書"),
    ("Amos",          "アモス書"),
    ("Obadiah",       "オバデヤ書"),
    ("Jonah",         "ヨナ書"),
    ("Micah",         "ミカ書"),
    ("Nahum",         "ナホム書"),
    ("Habakkuk",      "ハバクク書"),
    ("Zephaniah",     "ゼパニヤ書"),
    ("Haggai",        "ハガイ書"),
    ("Zechariah",     "ゼカリヤ書"),
    ("Malachi",       "マラキ書"),
    # 新約 (27冊)
    ("Matthew",       "マタイ"),
    ("Mark",          "マルコ"),
    ("Luke",          "ルカ"),
    ("John",          "ヨハネ"),
    ("Acts",          "使徒の働き"),
    ("Romans",        "ローマ"),
    ("1Corinthians",  "コリント一"),
    ("2Corinthians",  "コリント二"),
    ("Galatians",     "ガラテヤ"),
    ("Ephesians",     "エペソ"),
    ("Philippians",   "ピリピ"),
    ("Colossians",    "コロサイ"),
    ("1Thessalonians","テサロニケ一"),
    ("2Thessalonians","テサロニケ二"),
    ("1Timothy",      "テモテ一"),
    ("2Timothy",      "テモテ二"),
    ("Titus",         "テトス"),
    ("Philemon",      "ピレモン"),
    ("Hebrews",       "ヘブル"),
    ("James",         "ヤコブ"),
    ("1Peter",        "ペテロ一"),
    ("2Peter",        "ペテロ二"),
    ("1John",         "ヨハネ一"),
    ("2John",         "ヨハネ二"),
    ("3John",         "ヨハネ三"),
    ("Jude",          "ユダ"),
    ("Revelation",    "黙示録"),
]

OT_BOOKS = {b[0] for b in BOOKS[:39]}

def fetch_book(book_en):
    url = f"{BASE_URL}/{book_en}.json"
    try:
        with urllib.request.urlopen(url, timeout=10) as res:
            return json.loads(res.read().decode())
    except Exception as e:
        print(f"  ERROR: {e}")
        return None

def convert(raw, book_en, book_ja):
    """GitHubのJSON形式 → Verbumの内部形式に変換"""
    testament = "old" if book_en in OT_BOOKS else "new"
    chapters = {}
    for ch in raw.get("chapters", []):
        ch_num = int(ch["chapter"])
        verses = [{"v": int(v["verse"]), "t": v["text"]} for v in ch["verses"]]
        chapters[ch_num] = {"kjv": verses}
    return {
        "id": book_en.lower(),
        "nameEn": book_en,
        "nameJa": book_ja,
        "testament": testament,
        "chapters": chapters
    }

def main():
    os.makedirs("data/kjv", exist_ok=True)
    success, failed = [], []

    for i, (book_en, book_ja) in enumerate(BOOKS, 1):
        print(f"[{i:2d}/66] {book_en} ({book_ja})...", end=" ")
        raw = fetch_book(book_en)
        if raw:
            data = convert(raw, book_en, book_ja)
            path = f"data/kjv/{book_en.lower()}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            ch_count = len(data["chapters"])
            print(f"✓ {ch_count}章")
            success.append(book_en)
        else:
            print("✗ 失敗")
            failed.append(book_en)
        time.sleep(0.3)  # レート制限対策

    # インデックスファイル生成
    index = [{"id": b.lower(), "nameEn": b, "nameJa": j,
              "testament": "old" if b in OT_BOOKS else "new"}
             for b, j in BOOKS]
    with open("data/kjv/index.json", "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"\n完了: {len(success)}/66冊取得")
    if failed:
        print(f"失敗: {failed}")

if __name__ == "__main__":
    main()
