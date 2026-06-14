#!/usr/bin/env python3
"""
scrollmapper/bible_databases から 口語訳 (JapKougo) を取得して
プロジェクト形式に変換するスクリプト

scrollmapper のデータ形式:
{
  "books": [{"id": 1, "name": "Genesis"}, ...],
  "verses": [{"book_id": 1, "chapter": 1, "verse": 1, "text": "..."}, ...]
}
"""
import json
import urllib.request
import urllib.error
from pathlib import Path

# 書籍名マッピング (scrollmapper ID → ファイル名)
BOOK_FILE_NAMES = {
    1: "genesis", 2: "exodus", 3: "leviticus", 4: "numbers", 5: "deuteronomy",
    6: "joshua", 7: "judges", 8: "ruth", 9: "1samuel", 10: "2samuel",
    11: "1kings", 12: "2kings", 13: "1chronicles", 14: "2chronicles",
    15: "ezra", 16: "nehemiah", 17: "esther", 18: "job", 19: "psalms", 20: "proverbs",
    21: "ecclesiastes", 22: "song", 23: "isaiah", 24: "jeremiah", 25: "lamentations",
    26: "daniel", 27: "ezekiel", 28: "hosea", 29: "joel", 30: "amos",
    31: "obadiah", 32: "jonah", 33: "micah", 34: "nahum", 35: "habakkuk",
    36: "zephaniah", 37: "haggai", 38: "zechariah", 39: "malachi",
    40: "matthew", 41: "mark", 42: "luke", 43: "john", 44: "acts",
    45: "romans", 46: "1corinthians", 47: "2corinthians", 48: "galatians",
    49: "ephesians", 50: "philippians", 51: "colossians", 52: "1thessalonians",
    53: "2thessalonians", 54: "1timothy", 55: "2timothy", 56: "titus",
    57: "philemon", 58: "hebrews", 59: "james", 60: "1peter",
    61: "2peter", 62: "1john", 63: "2john", 64: "3john",
    65: "jude", 66: "revelation"
}

def fetch_json(url):
    """URL から JSON を取得"""
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.URLError as e:
        print(f"URLError: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    output_dir = Path(__file__).parent.parent / "data" / "japanese"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Fetching JapKougo data from scrollmapper...")
    url = "https://raw.githubusercontent.com/scrollmapper/bible_databases/master/formats/json/ja-JapKougo/ja-JapKougo.json"

    data = fetch_json(url)
    if not data:
        print("Failed to fetch data. Trying alternative approach...")
        print("Note: scrollmapper may have large files. Consider downloading manually from:")
        print("  https://github.com/scrollmapper/bible_databases/tree/master/formats/json/ja-JapKougo")
        return False

    print(f"✓ Fetched data. Processing {len(data.get('verses', []))} verses...")

    # 書籍ごとに整理
    books_data = {}
    for verse_obj in data.get('verses', []):
        book_id = verse_obj.get('book_id')
        chapter = verse_obj.get('chapter')
        verse_num = verse_obj.get('verse')
        text = verse_obj.get('text', '')

        if not book_id or not chapter:
            continue

        book_name = BOOK_FILE_NAMES.get(book_id, f"book{book_id}")

        if book_name not in books_data:
            books_data[book_name] = {}

        ch_str = str(chapter)
        if ch_str not in books_data[book_name]:
            books_data[book_name][ch_str] = {"japanese": []}

        books_data[book_name][ch_str]["japanese"].append({
            "v": verse_num,
            "t": text
        })

    # ファイルに保存
    count = 0
    for book_name, chapters in sorted(books_data.items()):
        filename = output_dir / f"{book_name}.json"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(chapters, f, ensure_ascii=False, indent=2)
            count += 1
            print(f"✓ {filename.name}")
        except Exception as e:
            print(f"✗ {filename.name}: {e}")

    print(f"\n✅ Successfully saved {count}/66 books")
    return count == 66

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
