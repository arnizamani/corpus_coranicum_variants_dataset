#!/usr/bin/env python3
"""Find cases where one transmitter has multiple variants for the same word."""

import json
import csv
from pathlib import Path
from collections import defaultdict

def find_multiple_variants():
    input_file = Path(__file__).resolve().parent.parent.parent / "data" / "all_variants_fixed.json"
    output_file = Path(__file__).resolve().parent.parent.parent / "data" / "multiple_variants.csv"
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cases = []
    
    for verse in data:
        surah = verse['surah']
        verse_num = verse['verse']
        
        # Get at-Taisīr variants
        taisir = [v for v in verse.get('variants', []) 
                 if v.get('work') == 'ad-Dānī (gest. 1053): at-Taisīr']
        
        # Group by reader and word position
        reader_words = defaultdict(lambda: defaultdict(list))
        
        for variant in taisir:
            reader = variant.get('reader', '').strip()
            if not reader:
                continue
            
            # Only process transmitters (those with parentheses) and exclude Hafs
            if '(' not in reader or reader == '5 ʿĀṣim (Ḥafṣ)':
                continue
            
            for word_pos, word in variant.get('words', {}).items():
                reader_words[reader][word_pos].append(word)
        
        # Find duplicates
        for reader, words in reader_words.items():
            for word_pos, word_list in words.items():
                if len(word_list) > 1:
                    # Check if they're actually different
                    unique_words = set(word_list)
                    if len(unique_words) > 1:
                        cases.append({
                            'surah': surah,
                            'verse': verse_num,
                            'word': word_pos,
                            'transmitter': reader,
                            'variant_count': len(unique_words),
                            'variants': ' | '.join(sorted(unique_words))
                        })
    
    # Write to CSV
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['surah', 'verse', 'word', 'transmitter', 'variant_count', 'variants'], lineterminator='\n')
        writer.writeheader()
        writer.writerows(cases)
    
    print(f"Exported {len(cases)} cases to {output_file}")
    
    # Print summary by transmitter
    transmitter_counts = defaultdict(int)
    for case in cases:
        transmitter_counts[case['transmitter']] += 1
    
    print(f"\nSummary by transmitter:")
    for trans, count in sorted(transmitter_counts.items(), key=lambda x: -x[1]):
        print(f"  {trans}: {count}")
    
    return cases


if __name__ == "__main__":
    find_multiple_variants()
