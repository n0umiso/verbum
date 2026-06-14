#!/usr/bin/env python3
"""
Merge original language texts with KJV translations.
Combines data/original/ with data/kjv/ into data/merged/
"""

import json
import os
from pathlib import Path
from typing import Dict


def merge_texts(kjv_dir: str, original_dir: str, output_dir: str):
    """Merge original language texts with KJV"""

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    kjv_files = sorted([f for f in os.listdir(kjv_dir) if f.endswith('.json')])
    original_files = sorted([f for f in os.listdir(original_dir) if f.endswith('.json')])

    merged_count = 0
    kjv_only = []
    original_only = []

    # Track which books have been merged
    merged_books = set()

    print("Merging texts...\n")

    # Process all original texts
    for orig_file in original_files:
        book_id = orig_file.replace('.json', '')

        # Load original
        orig_path = os.path.join(original_dir, orig_file)
        with open(orig_path, 'r', encoding='utf-8') as f:
            original_data = json.load(f)

        # Check if KJV exists
        kjv_file = orig_file
        kjv_path = os.path.join(kjv_dir, kjv_file)

        if os.path.exists(kjv_path):
            # Load KJV
            with open(kjv_path, 'r', encoding='utf-8') as f:
                kjv_data = json.load(f)

            # Merge chapters
            merged = {
                "id": original_data.get("id"),
                "nameEn": original_data.get("nameEn"),
                "nameJa": original_data.get("nameJa"),
                "testament": original_data.get("testament"),
                "chapters": {}
            }

            # Get all chapter numbers
            all_chapters = set(original_data.get("chapters", {}).keys())
            all_chapters.update(kjv_data.get("chapters", {}).keys())

            for chapter in sorted(all_chapters, key=int):
                orig_ch = original_data.get("chapters", {}).get(chapter, {})
                kjv_ch = kjv_data.get("chapters", {}).get(chapter, {})

                merged["chapters"][chapter] = {
                    "kjv": kjv_ch.get("kjv", []),
                    "original": orig_ch.get("original", [])
                }

            # Save merged
            output_path = os.path.join(output_dir, orig_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(merged, f, ensure_ascii=False, indent=2)

            print(f"  ✓ {book_id}")
            merged_count += 1
            merged_books.add(book_id)

        else:
            original_only.append(book_id)
            # Still save with structure but mark as original-only
            output_path = os.path.join(output_dir, orig_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(original_data, f, ensure_ascii=False, indent=2)
            print(f"  ⚠ {book_id} (original only)")

    # Check for KJV-only books
    for kjv_file in kjv_files:
        book_id = kjv_file.replace('.json', '')
        if book_id not in merged_books:
            kjv_only.append(book_id)
            # Copy KJV as-is
            kjv_path = os.path.join(kjv_dir, kjv_file)
            output_path = os.path.join(output_dir, kjv_file)
            with open(kjv_path, 'r', encoding='utf-8') as f:
                kjv_data = json.load(f)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(kjv_data, f, ensure_ascii=False, indent=2)
            print(f"  ⚠ {book_id} (KJV only)")

    print(f"\n{'='*60}")
    print(f"✓ Merge Complete: {merged_count} books merged")
    if original_only:
        print(f"⚠ Original-only books: {len(original_only)}")
    if kjv_only:
        print(f"⚠ KJV-only books: {len(kjv_only)}")
    print(f"{'='*60}")

    return merged_count


def main():
    project_dir = str(Path(__file__).resolve().parent.parent)
    kjv_dir = os.path.join(project_dir, "data", "kjv")
    original_dir = os.path.join(project_dir, "data", "original")
    output_dir = os.path.join(project_dir, "data", "merged")

    print("="*60)
    print("Merging Original Texts with KJV")
    print("="*60 + "\n")

    if not os.path.exists(original_dir):
        print(f"Error: {original_dir} does not exist")
        print("Run fetch_original_complete.py first")
        return

    merge_texts(kjv_dir, original_dir, output_dir)

    print("\nMerged texts saved to:")
    print(f"  {output_dir}")


if __name__ == "__main__":
    main()
