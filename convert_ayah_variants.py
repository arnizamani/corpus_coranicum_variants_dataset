#!/usr/bin/env python3
"""Convert variant ayah ends Excel to CSV with word positions from Cairo Quran."""

import json
import csv
import openpyxl
from pathlib import Path
import re


def normalize_arabic(text):
    """Normalize Arabic text for matching (remove tashkeel, normalize hamza/alif)."""
    if not text:
        return ""
    
    # Remove tashkeel (diacritics) and tatweel
    text = re.sub(r'[\u064B-\u065F\u0670\u0640]', '', text)
    
    # Normalize alif variants
    text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ٱ', 'ا')
    
    # Normalize hamza
    text = text.replace('ء', '').replace('ؤ', 'و').replace('ئ', 'ي')
    
    # Normalize ya/alif maqsura
    text = text.replace('ى', 'ي')
    
    # Normalize taa marbuta
    text = text.replace('ة', 'ه')
    
    # Remove spaces
    text = text.replace(' ', '')
    
    return text


def find_word_position(surah, words_text, cairo_data):
    """Find the verse and word position for the given Arabic text."""
    normalized_search = normalize_arabic(words_text)
    
    # Get all verses for this surah
    surah_verses = [v for v in cairo_data['verses'] if v['surah'] == surah]
    
    best_match = None
    best_score = 0
    
    for verse in surah_verses:
        verse_num = verse['verse']
        verse_words = verse['words']
        
        # Build full verse text
        full_verse = normalize_arabic(''.join([w['arabic'] for w in verse_words]))
        
        # Check if search text appears in verse
        if normalized_search in full_verse:
            # Find which word contains the end of the search phrase
            pos = full_verse.find(normalized_search)
            end_pos = pos + len(normalized_search)
            
            # Count characters to find word position
            char_count = 0
            for word in verse_words:
                word_text = normalize_arabic(word['arabic'])
                char_count += len(word_text)
                if char_count >= end_pos:
                    return {
                        'verse': verse_num,
                        'word_position': word['position'],
                        'score': 1.0
                    }
        
        # Fallback: try partial matching with windows
        for start_idx in range(len(verse_words)):
            for window_size in range(1, min(8, len(verse_words) - start_idx + 1)):
                window_words = verse_words[start_idx:start_idx + window_size]
                window_text = ''.join([normalize_arabic(w['arabic']) for w in window_words])
                
                # Calculate similarity
                if normalized_search in window_text:
                    score = len(normalized_search) / len(window_text)
                elif window_text in normalized_search:
                    score = len(window_text) / len(normalized_search)
                else:
                    # Check overlap
                    overlap = 0
                    for i in range(min(len(normalized_search), len(window_text))):
                        if i < len(normalized_search) and i < len(window_text):
                            if normalized_search[i] == window_text[i]:
                                overlap += 1
                    score = overlap / max(len(normalized_search), len(window_text))
                
                if score > best_score:
                    best_score = score
                    best_match = {
                        'verse': verse_num,
                        'word_position': window_words[-1]['position'],
                        'score': score
                    }
    
    return best_match


def convert_to_csv():
    """Convert Excel file to CSV with word positions."""
    script_dir = Path(__file__).parent
    excel_path = script_dir.parent / "Quran_corpus_10readings/Variant ends of ayaat.xlsx"
    cairo_path = script_dir / "cairo_quran.json"
    output_path = script_dir / "ayah_numbering_variants.csv"
    
    # Load Cairo Quran data
    print("Loading Cairo Quran data...")
    with open(cairo_path, 'r', encoding='utf-8') as f:
        cairo_data = json.load(f)
    
    # Load Excel data
    print("Loading Excel data...")
    wb = openpyxl.load_workbook(excel_path)
    ws = wb['Data']
    
    # Prepare output
    results = []
    current_surah = None
    
    print("\nProcessing variants...")
    for row_num, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 2):
        surah_name, surah, words, madani1, madani2, makki, basari, shami, kufi = row
        
        if surah:
            current_surah = surah
        
        if not current_surah or not words:
            continue
        
        # Find word position
        match = find_word_position(current_surah, words, cairo_data)
        
        if not match:
            print(f"  Warning: Could not find match for {current_surah}:{words[:30]}...")
            continue
        
        if match['score'] < 0.7:
            print(f"  Warning: Low confidence match ({match['score']:.2f}) for {current_surah}:{match['verse']}:{words[:30]}...")
        
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
        ])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"✓ Saved to {output_path}")
    print(f"✓ Total entries: {len(results)}")
    
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
