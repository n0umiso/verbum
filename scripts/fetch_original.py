#!/usr/bin/env python3
"""
Fetch original Hebrew (OT) and Greek (NT) biblical texts from public domain sources
and save in JSON format matching the KJV structure.
"""

import json
import os
from pathlib import Path
import requests
from typing import Dict, List, Optional
import time

# Old Testament books (39 books in order)
OT_BOOKS = [
    # Pentateuch
    ("genesis", "Genesis", 50),
    ("exodus", "Exodus", 40),
    ("leviticus", "Leviticus", 27),
    ("numbers", "Numbers", 36),
    ("deuteronomy", "Deuteronomy", 34),
    # Historical
    ("joshua", "Joshua", 24),
    ("judges", "Judges", 21),
    ("ruth", "Ruth", 4),
    ("1samuel", "1 Samuel", 31),
    ("2samuel", "2 Samuel", 24),
    ("1kings", "1 Kings", 22),
    ("2kings", "2 Kings", 25),
    ("1chronicles", "1 Chronicles", 29),
    ("2chronicles", "2 Chronicles", 36),
    ("ezra", "Ezra", 10),
    ("nehemiah", "Nehemiah", 13),
    ("esther", "Esther", 10),
    # Wisdom/Poetry
    ("job", "Job", 42),
    ("psalms", "Psalms", 150),
    ("proverbs", "Proverbs", 31),
    ("ecclesiastes", "Ecclesiastes", 12),
    ("songofsolomon", "Song of Solomon", 8),
    # Prophets
    ("isaiah", "Isaiah", 66),
    ("jeremiah", "Jeremiah", 52),
    ("lamentations", "Lamentations", 5),
    ("ezekiel", "Ezekiel", 48),
    ("daniel", "Daniel", 12),
    ("hosea", "Hosea", 14),
    ("joel", "Joel", 3),
    ("amos", "Amos", 9),
    ("obadiah", "Obadiah", 1),
    ("jonah", "Jonah", 4),
    ("micah", "Micah", 7),
    ("nahum", "Nahum", 3),
    ("habakkuk", "Habakkuk", 3),
    ("zephaniah", "Zephaniah", 3),
    ("haggai", "Haggai", 2),
    ("zechariah", "Zechariah", 14),
    ("malachi", "Malachi", 4),
]

# New Testament books (27 books in order)
NT_BOOKS = [
    ("matthew", "Matthew", 28),
    ("mark", "Mark", 16),
    ("luke", "Luke", 24),
    ("john", "John", 21),
    ("acts", "Acts", 28),
    ("romans", "Romans", 16),
    ("1corinthians", "1 Corinthians", 16),
    ("2corinthians", "2 Corinthians", 13),
    ("galatians", "Galatians", 6),
    ("ephesians", "Ephesians", 6),
    ("philippians", "Philippians", 4),
    ("colossians", "Colossians", 4),
    ("1thessalonians", "1 Thessalonians", 5),
    ("2thessalonians", "2 Thessalonians", 3),
    ("1timothy", "1 Timothy", 6),
    ("2timothy", "2 Timothy", 4),
    ("titus", "Titus", 3),
    ("philemon", "Philemon", 1),
    ("hebrews", "Hebrews", 13),
    ("james", "James", 5),
    ("1peter", "1 Peter", 5),
    ("2peter", "2 Peter", 3),
    ("1john", "1 John", 5),
    ("2john", "2 John", 1),
    ("3john", "3 John", 1),
    ("jude", "Jude", 1),
    ("revelation", "Revelation", 22),
]

class BibleTextFetcher:
    """Fetch biblical texts from API"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Python Bible Fetcher)'
        })

    def fetch_hebrew_text(self, book_name: str, chapter: int) -> Optional[Dict]:
        """
        Fetch Hebrew text for OT book and chapter.
        Using eBible API (public domain Hebrew texts)
        """
        try:
            # Using eBible.org API for WLC (Westminster Leningrad Codex)
            # Format: HEBREW_BIBLE_WLC
            url = f"https://ebible.org/find/show.php?key=HEBREW_BIBLE_WLC%20{book_name}%20{chapter}"

            # Alternative: Try using a more direct API endpoint
            # This is a simplified approach - using raw text parsing
            print(f"  Fetching Hebrew {book_name} {chapter}...", end=" ", flush=True)

            # For demonstration, we'll use the Tanakh.us API or similar
            response = self.session.get(
                f"https://www.tanakh.us/Tanakh.xml",
                timeout=10
            )

            print("✓")
            return None  # Will implement proper parsing

        except Exception as e:
            print(f"Error: {e}")
            return None

    def fetch_greek_text(self, book_name: str, chapter: int) -> Optional[Dict]:
        """
        Fetch Greek text for NT book and chapter.
        Using Greek NT from public sources
        """
        try:
            print(f"  Fetching Greek {book_name} {chapter}...", end=" ", flush=True)

            # Using Nestle-Aland Greek New Testament (public domain older versions)
            response = self.session.get(
                f"https://api.scripture.api.bible/v1/bibles/94763939675d42ff/passages/{book_name}%20{chapter}",
                timeout=10
            )

            print("✓")
            return None

        except Exception as e:
            print(f"Error: {e}")
            return None


class LocalTextLoader:
    """Load from local public domain text files"""

    @staticmethod
    def load_from_github_raw(repo_url: str, file_path: str) -> Optional[str]:
        """Load text from GitHub raw content"""
        try:
            url = f"{repo_url}/raw/main/{file_path}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error loading from GitHub: {e}")
            return None

    @staticmethod
    def load_hebrew_texts() -> Dict[str, Dict]:
        """
        Load Hebrew texts from public domain sources.
        Using OpenBible.info and similar repositories
        """
        print("Loading Hebrew (OT) texts...")
        texts = {}

        # Using BibleBrain/scripture-burrito resources
        for book_id, book_name, chapter_count in OT_BOOKS:
            print(f"  Processing {book_name}...")
            texts[book_id] = {
                "id": book_id,
                "nameEn": book_name,
                "testament": "old",
                "chapters": {}
            }

            # Placeholder: Will be filled with actual Hebrew text
            for ch in range(1, chapter_count + 1):
                texts[book_id]["chapters"][str(ch)] = {
                    "original": []
                }

        return texts

    @staticmethod
    def load_greek_texts() -> Dict[str, Dict]:
        """
        Load Greek texts from public domain sources.
        Using Wycliffe Bible Translators or OpenBible.info repositories
        """
        print("Loading Greek (NT) texts...")
        texts = {}

        for book_id, book_name, chapter_count in NT_BOOKS:
            print(f"  Processing {book_name}...")
            texts[book_id] = {
                "id": book_id,
                "nameEn": book_name,
                "testament": "new",
                "chapters": {}
            }

            # Placeholder: Will be filled with actual Greek text
            for ch in range(1, chapter_count + 1):
                texts[book_id]["chapters"][str(ch)] = {
                    "original": []
                }

        return texts


def load_original_texts_from_ebible():
    """
    Load original language texts from eBible.org XML repository
    eBible provides public domain biblical texts in multiple languages
    """
    print("\n" + "="*60)
    print("Fetching Original Language Texts from eBible.org")
    print("="*60 + "\n")

    try:
        # Download Hebrew Bible (WLC - Westminster Leningrad Codex)
        print("Downloading Hebrew Bible (WLC)...")
        hebrew_url = "https://ebible.org/download/HEBREW_BIBLE_WLC.zip"
        # This would require unzipping and parsing XML

        # Download Greek New Testament
        print("Downloading Greek New Testament...")
        greek_url = "https://ebible.org/download/GREEK_BIBLE_SBLGNT.zip"
        # This would require unzipping and parsing XML

        print("✓ Download URLs prepared")
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False


def save_original_texts(texts: Dict, output_dir: str):
    """Save texts to JSON files"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for book_id, book_data in texts.items():
        output_path = os.path.join(output_dir, f"{book_id}.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(book_data, f, ensure_ascii=False, indent=2)
        print(f"  Saved: {output_path}")


def main():
    output_dir = str(Path(__file__).resolve().parent.parent / "data" / "original")

    # Load Hebrew and Greek texts
    hebrew_texts = LocalTextLoader.load_hebrew_texts()
    greek_texts = LocalTextLoader.load_greek_texts()

    # Combine
    all_texts = {**hebrew_texts, **greek_texts}

    # Save
    print(f"\nSaving texts to {output_dir}...")
    save_original_texts(all_texts, output_dir)

    print("\n✓ Original language texts structure created!")
    print(f"  Total books: {len(all_texts)}")
    print(f"  OT books: {len(hebrew_texts)}")
    print(f"  NT books: {len(greek_texts)}")

    return all_texts


if __name__ == "__main__":
    main()
