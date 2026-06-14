#!/usr/bin/env python3
"""
FujiHaruka/bible-api から 口語訳聖書データを取得してプロジェクト形式に変換
API: GET /:book/from/:fromChapter/:fromVerse/to/:toChapter/:toVerse
"""
import json
import urllib.request
import urllib.error
from pathlib import Path
import time

# 書籍マッピング (ファイル名 → API キー, 最大章数)
BOOKS = {
    "genesis": ("gen", 50),
    "exodus": ("exod", 40),
    "leviticus": ("lev", 27),
    "numbers": ("num", 36),
    "deuteronomy": ("deut", 34),
    "joshua": ("josh", 24),
    "judges": ("judg", 21),
    "ruth": ("ruth", 4),
    "1samuel": ("1sam", 31),
    "2samuel": ("2sam", 24),
    "1kings": ("1kgs", 22),
    "2kings": ("2kgs", 25),
    "1chronicles": ("1chr", 29),
    "2chronicles": ("2chr", 36),
    "ezra": ("ezra", 10),
    "nehemiah": ("neh", 13),
    "esther": ("esth", 10),
    "job": ("job", 42),
    "psalms": ("ps", 150),
    "proverbs": ("prov", 31),
    "ecclesiastes": ("eccl", 12),
    "song": ("song", 8),
    "isaiah": ("isa", 66),
    "jeremiah": ("jer", 52),
    "lamentations": ("lam", 5),
    "daniel": ("dan", 12),
    "ezekiel": ("ezek", 48),
    "hosea": ("hos", 14),
    "joel": ("joel", 3),
    "amos": ("amos", 9),
    "obadiah": ("obad", 1),
    "jonah": ("jonah", 4),
    "micah": ("mic", 7),
    "nahum": ("nah", 3),
    "habakkuk": ("hab", 3),
    "zephaniah": ("zeph", 3),
    "haggai": ("hag", 2),
    "zechariah": ("zech", 14),
    "malachi": ("mal", 4),
    "matthew": ("matt", 28),
    "mark": ("mark", 16),
    "luke": ("luke", 24),
    "john": ("john", 21),
    "acts": ("acts", 28),
    "romans": ("rom", 16),
    "1corinthians": ("1cor", 16),
    "2corinthians": ("2cor", 13),
    "galatians": ("gal", 6),
    "ephesians": ("eph", 6),
    "philippians": ("phil", 4),
    "colossians": ("col", 4),
    "1thessalonians": ("1thess", 5),
    "2thessalonians": ("2thess", 3),
    "1timothy": ("1tim", 6),
    "2timothy": ("2tim", 4),
    "titus": ("titus", 3),
    "philemon": ("phlm", 1),
    "hebrews": ("heb", 13),
    "james": ("jas", 5),
    "1peter": ("1pet", 5),
    "2peter": ("2pet", 3),
    "1john": ("1john", 5),
    "2john": ("2john", 1),
    "3john": ("3john", 1),
    "jude": ("jude", 1),
    "revelation": ("rev", 22),
}

BASE_URL = "http://localhost:3000"  # デフォルト - FujiHaruka の API

def fetch_chapter(book_key, chapter):
    """特定の章のデータを取得"""
    url = f"{BASE_URL}/{book_key}/from/{chapter}/1/to/{chapter}/999"
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data if isinstance(data, list) else [data]
    except Exception as e:
        print(f"  ✗ Chapter {chapter}: {e}")
        return []

def fetch_from_public_api(book_key, max_chapter):
    """公開 API から全章を取得"""
    print(f"Fetching {book_key} ({max_chapter} chapters)...")
    book_data = {}

    for ch in range(1, max_chapter + 1):
        verses = fetch_chapter(book_key, ch)
        if verses:
            ch_str = str(ch)
            book_data[ch_str] = {
                "japanese": [
                    {"v": v.get("verse", i+1), "t": v.get("text", "")}
                    for i, v in enumerate(verses)
                ]
            }
            print(f"  ✓ Chapter {ch}: {len(verses)} verses")
        else:
            print(f"  ✗ Chapter {ch}: no data")
        time.sleep(0.1)  # Rate limit

    return book_data

def generate_sample_data():
    """サンプルデータを生成（API が利用不可の場合用）"""
    print("⚠️  API が利用不可。サンプルデータを生成中...")

    sample = {
        "1": {
            "japanese": [
                {"v": 1, "t": "はじめに神は天と地とを創造された。"},
                {"v": 2, "t": "地は形なく、むなしく、暗黒が深淵の面にあり、神の霊が水の面に運行していた。"},
                {"v": 3, "t": "神は言われた、「光あれ」。すると光があった。"},
            ]
        },
        "2": {
            "japanese": [
                {"v": 1, "t": "こうして天と地と、その万象とが完成した。"},
            ]
        }
    }
    return sample

def main():
    output_dir = Path(__file__).parent.parent / "data" / "japanese"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("FujiHaruka/bible-api から口語訳聖書を取得")
    print("=" * 60)

    # ローカル API が利用可能か確認
    try:
        req = urllib.request.Request(f"{BASE_URL}/gen/1/1")
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req, timeout=5) as response:
            print(f"✓ API is running at {BASE_URL}\n")
            use_api = True
    except:
        print(f"⚠️  API at {BASE_URL} is not available")
        print("Note: FujiHaruka/bible-api を自分のマシンで起動してください")
        print("  cd ~/bible-api && npm start\n")
        use_api = False

    # 全書籍を処理
    success_count = 0
    for filename, (api_key, max_chapter) in sorted(BOOKS.items()):
        if use_api:
            book_data = fetch_from_public_api(api_key, max_chapter)
            if not book_data:
                print(f"✗ Failed to fetch {filename}")
                continue
        else:
            book_data = generate_sample_data() if filename == "genesis" else {}

        # ファイルに保存
        output_file = output_dir / f"{filename}.json"
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(book_data, f, ensure_ascii=False, indent=2)
            success_count += 1
            if use_api:
                print(f"✓ Saved {output_file.name}")
        except Exception as e:
            print(f"✗ Error saving {filename}: {e}")

    print(f"\n{'=' * 60}")
    print(f"✅ Completed: {success_count}/66 books saved")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
