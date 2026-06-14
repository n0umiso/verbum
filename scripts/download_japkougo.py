#!/usr/bin/env python3
"""
GitHub API を使って scrollmapper の JapKougo.json をダウンロード
"""
import json
import urllib.request
import urllib.error
from pathlib import Path
import time

def download_with_api():
    """GitHub API v3 を使って raw content をダウンロード"""
    # GitHub API のレート制限を考慮してヘッダーを設定
    url = "https://api.github.com/repos/scrollmapper/bible_databases/contents/formats/json/JapKougo.json?ref=master"

    print("Downloading JapKougo.json via GitHub API...")

    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        req.add_header('Accept', 'application/vnd.github.v3.raw')

        with urllib.request.urlopen(req, timeout=120) as response:
            content = response.read()
            print(f"✓ Downloaded {len(content) / 1024 / 1024:.1f} MB")
            return json.loads(content.decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        if e.code == 403:
            print("Rate limit exceeded. Try again later or use a GitHub token.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def convert_scrollmapper_format(data):
    """
    scrollmapper フォーマット { "books": [...], "verses": [...] }
    を
    アプリフォーマット { "1": { "japanese": [...] }, ... }
    に変換
    """
    if not isinstance(data, dict):
        print(f"Unexpected data type: {type(data)}")
        return {}

    # scrollmapper の書籍情報
    books_by_id = {}
    if "books" in data:
        for book in data["books"]:
            books_by_id[book["id"]] = {
                "name": book["name"],
                "short": book.get("short", ""),
            }

    # ファイル名マッピング
    BOOK_NAMES = {
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

    # 書籍ごとに整理
    books_data = {}
    verses = data.get("verses", [])
    print(f"Processing {len(verses)} verses...")

    for verse_obj in verses:
        book_id = verse_obj.get("book_id")
        chapter = verse_obj.get("chapter")
        verse_num = verse_obj.get("verse")
        text = verse_obj.get("text", "")

        if not book_id or not chapter or not verse_num:
            continue

        book_name = BOOK_NAMES.get(book_id, f"book{book_id}")

        if book_name not in books_data:
            books_data[book_name] = {}

        ch_str = str(chapter)
        if ch_str not in books_data[book_name]:
            books_data[book_name][ch_str] = {"japanese": []}

        books_data[book_name][ch_str]["japanese"].append({
            "v": verse_num,
            "t": text
        })

    return books_data

def main():
    output_dir = Path(__file__).parent.parent / "data" / "japanese"
    output_dir.mkdir(parents=True, exist_ok=True)

    # ダウンロード
    data = download_with_api()
    if not data:
        print("Failed to download data")
        return False

    # 変換
    print("Converting data...")
    books_data = convert_scrollmapper_format(data)

    if not books_data:
        print("Failed to convert data")
        return False

    # 既存ファイルをバックアップ
    import shutil
    backup_dir = output_dir.parent / "japanese_backup"
    if output_dir.exists():
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        shutil.copytree(output_dir, backup_dir)
        print(f"✓ Backed up existing files to {backup_dir.name}")

    # 新しいファイルを保存
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

    print(f"\n{'=' * 60}")
    print(f"✅ Successfully saved {count}/66 books")
    print(f"{'=' * 60}")
    return count > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
