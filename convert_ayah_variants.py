#!/usr/bin/env python3
"""Convert variant ayah ends Excel to CSV with word positions from Cairo Quran."""

import json
import csv
from pathlib import Path


def normalize_for_matching(text):
    """
    Normalize Arabic text using the same logic as match_rasm.
    This matches the simplified orthography used in the Excel file.
    """
    if not text:
        return ""

    # Remove all diacritics and special marks (comprehensive list)
    diacritics = [
        '\u064B', '\u064C', '\u064D', '\u064E', '\u064F', '\u0650', '\u0651',
        '\u0652', '\u0653', '\u0654', '\u0655', '\u0656', '\u0657', '\u0658',
        '\u0670', '\u0640', '\u06E5', '\u06E6', '\u06E7', '\u06E8', '\u06EA',
        '\u06EB', '\u06EC', '\u06ED', '\u08F0', '\u08F1', '\u08F2', '\u08F3',
        '\u202F', '\u2008', '_', '\u06D6', '\u06D7', '\u06D8', '\u06D9', '\u06DA',
        '\u06DB', '\u06DC', '\u06DD', '\u06DE', '\u06DF', '\u06E0', '\u06E1',
        '\u06E2', '\u06E3', '\u06E4', '\u08E3', '\u08E4', '\u08E5', '\u08E6',
        '\u08E7', '\u08E8', '\u08E9', '\u08EA', '\u08EB', '\u08EC', '\u08ED',
        '\u08EE', '\u08EF', '\u08F4', '\u08F5', '\u08F6', '\u08F7', '\u08F8',
        '\u08F9', '\u08FA', '\u08FB', '\u08FC', '\u08FD', '\u08FE', '\u08FF',
        '\u0674', '\u0673'  # Hamza above and below alif
    ]
    for d in diacritics:
        text = text.replace(d, '')

    # Normalize ALL alif variants to simple alif (including alif wasla)
    text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ٱ', 'ا')

    # Normalize hamza on waw/yeh to base letter
    text = text.replace('ؤ', 'و').replace('ئ', 'ى')

    # Remove standalone hamza
    text = text.replace('ء', '')

    # Normalize teh marbuta to heh
    text = text.replace('ة', 'ه')

    # Normalize yeh variants to alif maqsura
    text = text.replace('ي', 'ى').replace('ی', 'ى')

    # Remove spaces
    text = text.replace(' ', '')

    return text


def find_word_position_precise(surah, words_text, cairo_data):
    """Find the verse and word position using precise matching."""
    normalized_search = normalize_for_matching(words_text)

    # Special case: if search starts with "الرحيم" (from basmala), remove it
    # and only search for the rest at the beginning of the surah
    basmala_word = normalize_for_matching('الرحيم')
    if normalized_search.startswith(basmala_word):
        normalized_search = normalized_search[len(basmala_word):]
        # Only match at the very beginning of the surah (verse 1)
        surah_verses = [v for v in cairo_data['verses'] if v['surah'] == surah and v['verse'] == 1]
        if surah_verses:
            verse = surah_verses[0]
            first_word_normalized = normalize_for_matching(verse['words'][0]['arabic'])
            if first_word_normalized == normalized_search:
                return [{
                    'verse': 1,
                    'word_position': verse['words'][0]['position'],
                    'matched_text': verse['words'][0]['arabic']
                }]
        return []

    # Get all verses for this surah and build continuous text
    surah_verses = [v for v in cairo_data['verses'] if v['surah'] == surah]

    # Build a flat list of all words in the surah with their verse info
    all_words = []
    for verse in surah_verses:
        for word in verse['words']:
            all_words.append({
                'verse': verse['verse'],
                'position': word['position'],
                'arabic': word['arabic'],
                'normalized': normalize_for_matching(word['arabic'])
            })

    # Build full surah text once
    full_text = ''.join([w['normalized'] for w in all_words])

    matches = []

    # Find all occurrences of the search text
    search_positions = []

    # Try exact match
    pos = full_text.find(normalized_search)
    while pos != -1:
        search_positions.append((pos, pos + len(normalized_search), 'exact'))
        pos = full_text.find(normalized_search, pos + 1)

    # Try match without alifs if no exact match and search is long enough
    if not search_positions and len(normalized_search.replace('ا', '')) > 3:
        search_no_alif = normalized_search.replace('ا', '')
        text_no_alif = full_text.replace('ا', '')

        pos = text_no_alif.find(search_no_alif)
        while pos != -1:
            # Map back to original position
            orig_pos = 0
            no_alif_count = 0
            for i, c in enumerate(full_text):
                if c != 'ا':
                    if no_alif_count == pos:
                        orig_pos = i
                        break
                    no_alif_count += 1

            # Find end position
            end_pos = orig_pos
            chars_found = 0
            for i in range(orig_pos, len(full_text)):
                if full_text[i] != 'ا':
                    chars_found += 1
                    if chars_found == len(search_no_alif):
                        end_pos = i + 1
                        break

            search_positions.append((orig_pos, end_pos, 'no_alif'))
            pos = text_no_alif.find(search_no_alif, pos + 1)

    # Convert positions to word indices
    for start_pos, end_pos, match_type in search_positions:
        # Find which word the end position falls in
        char_count = 0
        for idx, word in enumerate(all_words):
            char_count += len(word['normalized'])
            if char_count >= end_pos:
                matches.append({
                    'verse': word['verse'],
                    'word_position': word['position'],
                    'matched_text': ''.join([w['arabic'] for w in all_words[max(0, idx-2):idx + 1]])
                })
                break

    return matches


def convert_to_csv():
    """Convert variant ayah ends CSV to output CSV with word positions."""
    script_dir = Path(__file__).parent
    input_csv_path = script_dir / "tests/ayah_variants_reference.csv"
    cairo_path = script_dir / "cairo_quran.json"
    output_path = script_dir / "ayah_numbering_variants.csv"

    # Load Cairo Quran data
    print("Loading Cairo Quran data...")
    with open(cairo_path, 'r', encoding='utf-8') as f:
        cairo_data = json.load(f)

    # Load input CSV data
    print("Loading input CSV data...")
    with open(input_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)

    # Prepare output
    results = []
    current_surah = None
    skipped = []
    used_locations = set()  # Track (surah, verse, word_pos) that have been used

    print("\nProcessing variants...")
    for row_num, row in enumerate(rows[1:], 2):
        if len(row) < 9:
            continue
        surah_name, surah, words, madani1, madani2, makki, basari, shami, kufi = row[:9]
        surah = int(surah) if surah else None

        def parse(v):
            return int(v) if v not in ('', None) else None
        madani1, madani2, makki, basari, shami, kufi = map(
            parse, [madani1, madani2, makki, basari, shami, kufi]
        )

        if surah:
            current_surah = surah
            used_locations = set()  # Reset for new surah

        if not current_surah or not words:
            continue

        # Find word position
        matches = find_word_position_precise(current_surah, words, cairo_data)

        if not matches:
            print(f"  Row {row_num}: No match for {current_surah}:{words[:40]}...")
            skipped.append((row_num, current_surah, words))
            continue

        # Filter out already used locations
        unused_matches = [m for m in matches if (current_surah, m['verse'], m['word_position']) not in used_locations]

        if not unused_matches:
            print(f"  Row {row_num}: All matches already used for {current_surah}:{words[:40]}...")
            skipped.append((row_num, current_surah, words))
            continue

        if len(unused_matches) > 1:
            print(f"  Row {row_num}: Multiple matches ({len(unused_matches)}) for {current_surah}:{words[:40]}, using first")

        # Use the first unused match (they're in verse order)
        match = unused_matches[0]
        used_locations.add((current_surah, match['verse'], match['word_position']))

        # Fill null values with Kufi value (agrees with reference)
        kufi_val = kufi if kufi is not None else 0
        results.append({
            'surah': current_surah,
            'verse': match['verse'],
            'word_position': match['word_position'],
            'madani1': madani1 if madani1 is not None else kufi_val,
            'madani2': madani2 if madani2 is not None else kufi_val,
            'makki': makki if makki is not None else kufi_val,
            'basari': basari if basari is not None else kufi_val,
            'shami': shami if shami is not None else kufi_val,
            'kufi': kufi_val
        })

        if row_num % 50 == 0:
            print(f"  Processed {row_num - 1} rows...")

    # Sort by surah, verse, word_position
    results.sort(key=lambda x: (x['surah'], x['verse'], x['word_position']))

    # Write to CSV
    print(f"\nWriting {len(results)} entries to CSV...")
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'surah', 'verse', 'word_position',
            'madani1', 'madani2', 'makki', 'basari', 'shami', 'kufi'
        ], lineterminator='\n')
        writer.writeheader()
        writer.writerows(results)

    print(f"✓ Saved to {output_path}")
    print(f"✓ Total entries: {len(results)}")
    print(f"✓ Skipped entries: {len(skipped)}")

    if skipped:
        print("\nSkipped entries (no unique match):")
        for row_num, surah, words in skipped[:10]:
            print(f"  Row {row_num}: Surah {surah}: {words[:50]}...")

    # Statistics
    reading_counts = {
        'madani1': sum(1 for r in results if r['madani1'] != 0),
        'madani2': sum(1 for r in results if r['madani2'] != 0),
        'makki': sum(1 for r in results if r['makki'] != 0),
        'basari': sum(1 for r in results if r['basari'] != 0),
        'shami': sum(1 for r in results if r['shami'] != 0),
        'kufi': sum(1 for r in results if r['kufi'] != 0)
    }

    print("\nVariant counts (non-zero):")
    for reading, count in reading_counts.items():
        print(f"  {reading}: {count}")


if __name__ == "__main__":
    convert_to_csv()
