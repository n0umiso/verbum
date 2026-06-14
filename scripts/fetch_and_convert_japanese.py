#!/usr/bin/env python3
"""
scrollmapper/bible_databases から JapKougo (口語訳) データを取得して
プロジェクト形式に変換するスクリプト
"""
import json
import os
import urllib.request
from pathlib import Path

# Bible books mapping (Bible abbreviations)
BOOK_NAMES = {
    "genesis": "Genesis", "exodus": "Exodus", "leviticus": "Leviticus",
    "numbers": "Numbers", "deuteronomy": "Deuteronomy", "joshua": "Joshua",
    "judges": "Judges", "ruth": "Ruth", "1samuel": "1 Samuel", "2samuel": "2 Samuel",
    "1kings": "1 Kings", "2kings": "2 Kings", "1chronicles": "1 Chronicles",
    "2chronicles": "2 Chronicles", "ezra": "Ezra", "nehemiah": "Nehemiah",
    "esther": "Esther", "job": "Job", "psalms": "Psalms", "proverbs": "Proverbs",
    "ecclesiastes": "Ecclesiastes", "song": "Song of Solomon", "isaiah": "Isaiah",
    "jeremiah": "Jeremiah", "lamentations": "Lamentations", "daniel": "Daniel",
    "ezekiel": "Ezekiel", "hosea": "Hosea", "joel": "Joel", "amos": "Amos",
    "obadiah": "Obadiah", "jonah": "Jonah", "micah": "Micah", "nahum": "Nahum",
    "habakkuk": "Habakkuk", "zephaniah": "Zephaniah", "haggai": "Haggai",
    "zechariah": "Zechariah", "malachi": "Malachi", "matthew": "Matthew",
    "mark": "Mark", "luke": "Luke", "john": "John", "acts": "Acts",
    "romans": "Romans", "1corinthians": "1 Corinthians", "2corinthians": "2 Corinthians",
    "galatians": "Galatians", "ephesians": "Ephesians", "philippians": "Philippians",
    "colossians": "Colossians", "1thessalonians": "1 Thessalonians",
    "2thessalonians": "2 Thessalonians", "1timothy": "1 Timothy", "2timothy": "2 Timothy",
    "titus": "Titus", "philemon": "Philemon", "hebrews": "Hebrews", "james": "James",
    "1peter": "1 Peter", "2peter": "2 Peter", "1john": "1 John", "2john": "2 John",
    "3john": "3 John", "jude": "Jude", "revelation": "Revelation"
}

def get_japanese_data(book_key):
    """GitHub から JapKougo JSON を取得"""
    url = f"https://raw.githubusercontent.com/scrollmapper/bible_databases/master/formats/json/ja-JapKougo/ja-JapKougo.json"

    try:
        print(f"Fetching from {url}...")
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def convert_to_app_format(scrollmapper_data):
    """scrollmapper フォーマットをアプリフォーマットに変換"""
    result = {}

    # scrollmapper のデータ構造: { "books": [...], "verses": [...] }
    if not scrollmapper_data or "verses" not in scrollmapper_data:
        print("Invalid data structure")
        return result

    # 書籍ごとにグループ化
    books_by_id = {}
    if "books" in scrollmapper_data:
        for book in scrollmapper_data["books"]:
            books_by_id[book["id"]] = book["name"]

    # 節をまとめる
    for verse in scrollmapper_data["verses"]:
        book_id = verse.get("book_id")
        chapter = verse.get("chapter")
        verse_num = verse.get("verse")
        text = verse.get("text", "")

        if not book_id or not chapter:
            continue

        book_name = books_by_id.get(book_id, f"Book{book_id}")

        # 書籍キーを作成
        book_key = book_name.lower().replace(" ", "").replace("-", "")

        if book_key not in result:
            result[book_key] = {}

        ch_str = str(chapter)
        if ch_str not in result[book_key]:
            result[book_key][ch_str] = {"japanese": []}

        result[book_key][ch_str]["japanese"].append({
            "v": verse_num,
            "t": text
        })

    return result

def main():
    output_dir = Path(__file__).parent.parent / "data" / "japanese"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Fetching Japanese Bible data from scrollmapper...")
    data = get_japanese_data("ja-JapKougo")

    if not data:
        print("Failed to fetch data")
        return

    print(f"Converting data...")
    converted = convert_to_app_format(data)

    if not converted:
        print("Failed to convert data")
        return

    # 書籍ごとにファイルを保存
    for book_key, chapters in converted.items():
        filename = output_dir / f"{book_key}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(chapters, f, ensure_ascii=False, indent=2)
        print(f"✓ Saved {filename}")

    print(f"\nDone! Converted {len(converted)} books")

if __name__ == "__main__":
    main()
