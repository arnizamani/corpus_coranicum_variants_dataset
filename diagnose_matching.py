#!/usr/bin/env python3
"""Diagnostic script to analyze word position matching quality."""

import json
import csv
import openpyxl
from pathlib import Path
import re
from collections import defaultdict


def normalize_arabic(text):
    """Normalize Arabic text for matching."""
    if not text:
        return ""
    
    text = re.sub(r'[\u064B-\u065F\u0670\u0640]', '', text)
    text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ٱ', 'ا')
    text = text.replace('ء', '').replace('ؤ', 'و').replace('ئ', 'ي')
    text = text.replace('ى', 'ي')
    text = text.replace('ة', 'ه')
    text = text.replace(' ', '')
    
    return text


def main():
    excel_path = Path("Quran_corpus_10readings/Variant ends of ayaat.xlsx")
    cairo_path = Path("corpus_coranicum_variants_dataset/cairo_quran.json")
    csv_path = Path("corpus_coranicum_variants_dataset/ayah_numbering_variants.csv")
    
    # Load Cairo Quran
    with open(cairo_path, 'r', encoding='utf-8') as f:
        cairo_data = json.load(f)
    
    # Build Cairo lookup
    cairo_lookup = {}
    for verse in cairo_data['verses']:
        key = (verse['surah'], verse['verse'])
        cairo_lookup[key] = verse['words']
    
    # Load Excel
    wb = openpyxl.load_workbook(excel_path)
    ws = wb['Data']
    
    excel_entries = []
    current_surah = None
    for row in ws.iter_rows(min_row=2, values_only=True):
        surah_name, surah, words, madani1, madani2, makki, basari, shami, kufi = row
        
        if surah:
            current_surah = surah
        
        if current_surah and words:
            excel_entries.append({
                'surah': current_surah,
                'words': words,
                'madani1': madani1,
                'kufi': kufi
            })
    
    # Load CSV
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        csv_entries = list(reader)
    
    # Find duplicates in CSV
    from collections import Counter
    locations = [(int(row['surah']), int(row['verse']), int(row['word_position'])) for row in csv_entries]
    duplicates = [loc for loc, count in Counter(locations).items() if count > 1]
    
    print(f"Total Excel entries: {len(excel_entries)}")
    print(f"Total CSV entries: {len(csv_entries)}")
    print(f"Duplicate locations in CSV: {len(duplicates)}\n")
    
    # Analyze each duplicate
    for dup_loc in duplicates:
        surah, verse, word_pos = dup_loc
        print(f"\n{'='*80}")
        print(f"DUPLICATE: Surah {surah}:{verse}, word position {word_pos}")
        print(f"{'='*80}")
        
        # Find Cairo words at this location
        cairo_words = cairo_lookup.get((surah, verse), [])
        if cairo_words:
            word_at_pos = next((w for w in cairo_words if w['position'] == word_pos), None)
            if word_at_pos:
                print(f"Cairo word at position {word_pos}: {word_at_pos['arabic']} ({word_at_pos['transliteration']})")
        
        # Find all CSV entries with this location
        csv_matches = [row for row in csv_entries if 
                      (int(row['surah']), int(row['verse']), int(row['word_position'])) == dup_loc]
        
        print(f"\nCSV has {len(csv_matches)} entries for this location:")
        for i, match in enumerate(csv_matches, 1):
            print(f"  Entry {i}: madani1={match['madani1']}, kufi={match['kufi']}")
        
        # Find Excel entries for this surah
        excel_matches = [e for e in excel_entries if e['surah'] == surah]
        print(f"\nExcel has {len(excel_matches)} entries for surah {surah}:")
        for i, match in enumerate(excel_matches, 1):
            normalized = normalize_arabic(match['words'])
            print(f"  Entry {i}: {match['words'][:40]}... (normalized: {normalized[:30]}...)")
            print(f"           madani1={match['madani1']}, kufi={match['kufi']}")
    
    # Check for low-confidence matches
    print(f"\n\n{'='*80}")
    print("CHECKING FOR POTENTIAL MATCHING ISSUES")
    print(f"{'='*80}\n")
    
    # Group Excel entries by surah
    by_surah = defaultdict(list)
    for entry in excel_entries:
        by_surah[entry['surah']].append(entry)
    
    # Find surahs with multiple entries
    multi_entry_surahs = {s: entries for s, entries in by_surah.items() if len(entries) > 1}
    
    print(f"Surahs with multiple Excel entries: {len(multi_entry_surahs)}")
    for surah in sorted(multi_entry_surahs.keys())[:10]:
        entries = multi_entry_surahs[surah]
        print(f"\nSurah {surah}: {len(entries)} entries")
        for entry in entries:
            print(f"  - {entry['words'][:50]}...")


if __name__ == "__main__":
    main()
