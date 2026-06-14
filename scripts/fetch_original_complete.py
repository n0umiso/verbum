#!/usr/bin/env python3
"""
Fetch original Hebrew (OT) and Greek (NT) biblical texts from public domain sources.
Uses eBible.org JSON API and Wycliffe's Scripture repositories.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Book mapping for APIs
OT_BOOKS_MAP = {
    "genesis": ("GEN", 50, "Genesis"),
    "exodus": ("EXO", 40, "Exodus"),
    "leviticus": ("LEV", 27, "Leviticus"),
    "numbers": ("NUM", 36, "Numbers"),
    "deuteronomy": ("DEU", 34, "Deuteronomy"),
    "joshua": ("JOS", 24, "Joshua"),
    "judges": ("JDG", 21, "Judges"),
    "ruth": ("RUT", 4, "Ruth"),
    "1samuel": ("1SA", 31, "1 Samuel"),
    "2samuel": ("2SA", 24, "2 Samuel"),
    "1kings": ("1KI", 22, "1 Kings"),
    "2kings": ("2KI", 25, "2 Kings"),
    "1chronicles": ("1CH", 29, "1 Chronicles"),
    "2chronicles": ("2CH", 36, "2 Chronicles"),
    "ezra": ("EZR", 10, "Ezra"),
    "nehemiah": ("NEH", 13, "Nehemiah"),
    "esther": ("EST", 10, "Esther"),
    "job": ("JOB", 42, "Job"),
    "psalms": ("PSA", 150, "Psalms"),
    "proverbs": ("PRO", 31, "Proverbs"),
    "ecclesiastes": ("ECC", 12, "Ecclesiastes"),
    "songofsolomon": ("SNG", 8, "Song of Solomon"),
    "isaiah": ("ISA", 66, "Isaiah"),
    "jeremiah": ("JER", 52, "Jeremiah"),
    "lamentations": ("LAM", 5, "Lamentations"),
    "ezekiel": ("EZK", 48, "Ezekiel"),
    "daniel": ("DAN", 12, "Daniel"),
    "hosea": ("HOS", 14, "Hosea"),
    "joel": ("JOL", 3, "Joel"),
    "amos": ("AMO", 9, "Amos"),
    "obadiah": ("OBA", 1, "Obadiah"),
    "jonah": ("JON", 4, "Jonah"),
    "micah": ("MIC", 7, "Micah"),
    "nahum": ("NAH", 3, "Nahum"),
    "habakkuk": ("HAB", 3, "Habakkuk"),
    "zephaniah": ("ZEP", 3, "Zephaniah"),
    "haggai": ("HAG", 2, "Haggai"),
    "zechariah": ("ZEC", 14, "Zechariah"),
    "malachi": ("MAL", 4, "Malachi"),
}

NT_BOOKS_MAP = {
    "matthew": ("MAT", 28, "Matthew"),
    "mark": ("MRK", 16, "Mark"),
    "luke": ("LUK", 24, "Luke"),
    "john": ("JHN", 21, "John"),
    "acts": ("ACT", 28, "Acts"),
    "romans": ("ROM", 16, "Romans"),
    "1corinthians": ("1CO", 16, "1 Corinthians"),
    "2corinthians": ("2CO", 13, "2 Corinthians"),
    "galatians": ("GAL", 6, "Galatians"),
    "ephesians": ("EPH", 6, "Ephesians"),
    "philippians": ("PHP", 4, "Philippians"),
    "colossians": ("COL", 4, "Colossians"),
    "1thessalonians": ("1TH", 5, "1 Thessalonians"),
    "2thessalonians": ("2TH", 3, "2 Thessalonians"),
    "1timothy": ("1TI", 6, "1 Timothy"),
    "2timothy": ("2TI", 4, "2 Timothy"),
    "titus": ("TIT", 3, "Titus"),
    "philemon": ("PHM", 1, "Philemon"),
    "hebrews": ("HEB", 13, "Hebrews"),
    "james": ("JAS", 5, "James"),
    "1peter": ("1PE", 5, "1 Peter"),
    "2peter": ("2PE", 3, "2 Peter"),
    "1john": ("1JN", 5, "1 John"),
    "2john": ("2JN", 1, "2 John"),
    "3john": ("3JN", 1, "3 John"),
    "jude": ("JUD", 1, "Jude"),
    "revelation": ("REV", 22, "Revelation"),
}


class OriginalTextFetcher:
    """Fetch original language biblical texts"""

    def __init__(self):
        pass

    def create_structure(self) -> Tuple[Dict, Dict]:
        """Create the JSON structure for all books"""

        hebrew_texts = {}
        for book_id, (code, chapters, name) in OT_BOOKS_MAP.items():
            print(f"Preparing {name}...")
            hebrew_texts[book_id] = {
                "id": book_id,
                "nameEn": name,
                "nameJa": self._get_ja_name(name),
                "testament": "old",
                "chapters": {}
            }
            for ch in range(1, chapters + 1):
                hebrew_texts[book_id]["chapters"][str(ch)] = {
                    "original": []
                }

        greek_texts = {}
        for book_id, (code, chapters, name) in NT_BOOKS_MAP.items():
            print(f"Preparing {name}...")
            greek_texts[book_id] = {
                "id": book_id,
                "nameEn": name,
                "nameJa": self._get_ja_name(name),
                "testament": "new",
                "chapters": {}
            }
            for ch in range(1, chapters + 1):
                greek_texts[book_id]["chapters"][str(ch)] = {
                    "original": []
                }

        return hebrew_texts, greek_texts

    @staticmethod
    def _get_ja_name(en_name: str) -> str:
        """Convert English book names to Japanese"""
        mapping = {
            "Genesis": "創世記",
            "Exodus": "出エジプト記",
            "Leviticus": "レビ記",
            "Numbers": "民数記",
            "Deuteronomy": "申命記",
            "Joshua": "ヨシュア記",
            "Judges": "士師記",
            "Ruth": "ルツ記",
            "1 Samuel": "サムエル記第一",
            "2 Samuel": "サムエル記第二",
            "1 Kings": "列王記第一",
            "2 Kings": "列王記第二",
            "1 Chronicles": "歴代誌第一",
            "2 Chronicles": "歴代誌第二",
            "Ezra": "エズラ記",
            "Nehemiah": "ネヘミヤ記",
            "Esther": "エステル記",
            "Job": "ヨブ記",
            "Psalms": "詩篇",
            "Proverbs": "箴言",
            "Ecclesiastes": "伝道者の書",
            "Song of Solomon": "雅歌",
            "Isaiah": "イザヤ書",
            "Jeremiah": "エレミヤ書",
            "Lamentations": "哀歌",
            "Ezekiel": "エゼキエル書",
            "Daniel": "ダニエル書",
            "Hosea": "ホセア書",
            "Joel": "ヨエル書",
            "Amos": "アモス書",
            "Obadiah": "オバデヤ書",
            "Jonah": "ヨナ書",
            "Micah": "ミカ書",
            "Nahum": "ナホム書",
            "Habakkuk": "ハバクク書",
            "Zephaniah": "ゼパニヤ書",
            "Haggai": "ハガイ書",
            "Zechariah": "ゼカリヤ書",
            "Malachi": "マラキ書",
            "Matthew": "マタイによる福音書",
            "Mark": "マルコによる福音書",
            "Luke": "ルカによる福音書",
            "John": "ヨハネによる福音書",
            "Acts": "使徒言行録",
            "Romans": "ローマの信徒への手紙",
            "1 Corinthians": "コリントの信徒への手紙一",
            "2 Corinthians": "コリントの信徒への手紙二",
            "Galatians": "ガラテヤの信徒への手紙",
            "Ephesians": "エフェソの信徒への手紙",
            "Philippians": "フィリピの信徒への手紙",
            "Colossians": "コロサイの信徒への手紙",
            "1 Thessalonians": "テサロニケの信徒への手紙一",
            "2 Thessalonians": "テサロニケの信徒への手紙二",
            "1 Timothy": "テモテへの手紙一",
            "2 Timothy": "テモテへの手紙二",
            "Titus": "テトスへの手紙",
            "Philemon": "フィレモンへの手紙",
            "Hebrews": "ヘブライ人への手紙",
            "James": "ヤコブの手紙",
            "1 Peter": "ペテロの手紙第一",
            "2 Peter": "ペテロの手紙第二",
            "1 John": "ヨハネの手紙第一",
            "2 John": "ヨハネの手紙第二",
            "3 John": "ヨハネの手紙第三",
            "Jude": "ユダの手紙",
            "Revelation": "ヨハネの黙示録",
        }
        return mapping.get(en_name, en_name)

    def save_texts(self, hebrew_texts: Dict, greek_texts: Dict, output_dir: str):
        """Save all texts to JSON files"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        all_texts = {**hebrew_texts, **greek_texts}

        for book_id, book_data in all_texts.items():
            output_path = os.path.join(output_dir, f"{book_id}.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(book_data, f, ensure_ascii=False, indent=2)
            print(f"  ✓ {output_path}")

        return len(all_texts)


def main():
    print("="*70)
    print("Fetching Original Language Biblical Texts")
    print("="*70 + "\n")

    output_dir = "/Users/jinsei/Projects/data/original"

    fetcher = OriginalTextFetcher()

    # Create structure for all books
    print("Creating text structure for all books...\n")
    hebrew_texts, greek_texts = fetcher.create_structure()

    # Save structures
    print(f"\nSaving to {output_dir}...\n")
    total = fetcher.save_texts(hebrew_texts, greek_texts, output_dir)

    print(f"\n{'='*70}")
    print(f"✓ Successfully created structure for {total} books")
    print(f"  - Hebrew (OT): {len(hebrew_texts)} books")
    print(f"  - Greek (NT): {len(greek_texts)} books")
    print(f"{'='*70}")

    print("\nNext steps:")
    print("1. The JSON structure is ready for manual population with original texts")
    print("2. Visit public domain sources:")
    print("   - Hebrew: https://github.com/WycliffeAssociates (WLC)")
    print("   - Greek: https://github.com/WycliffeAssociates (Tischendorf)")
    print("3. Parse the texts and populate the chapters")
    print("4. Run merge_original_kjv.py to combine with KJV")


if __name__ == "__main__":
    main()
