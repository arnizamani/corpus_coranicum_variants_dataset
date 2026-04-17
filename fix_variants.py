#!/usr/bin/env python3
"""Fix issues in all_variants.json downloaded from Corpus Coranicum.

This script fixes several data quality issues:
1. Links transmitters to their reciters (e.g., "ad-Dūrī" -> "3 Abū ʿAmr (ad-Dūrī)")
2. Removes duplicate reciter entries that cause incorrect transmitter linking
3. Fixes 75:1 where only al-Bazzī differs (reads both "la-" and "lā"), not Ibn Kaṯīr
"""

import json
from pathlib import Path


def fix_variants():
    input_file = Path(__file__).parent / "all_variants.json"
    output_file = Path(__file__).parent / "all_variants_fixed.json"
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for verse in data:
        surah = verse.get('surah')
        verse_num = verse.get('verse')
        variants = verse.get('variants', [])
        
        # Get indices of at-Taisīr variants
        taisir_indices = [i for i, v in enumerate(variants) 
                         if v.get('work') == 'ad-Dānī (gest. 1053): at-Taisīr']
        
        # Fix 1: Special case for 75:1 - only al-Bazzī differs
        if surah == 75 and verse_num == 1:
            # Remove duplicate Ibn Kaṯīr and fix readings
            to_remove = []
            for i, idx in enumerate(taisir_indices):
                reader = variants[idx].get('reader', '')
                if reader == '2 Ibn Kaṯīr':
                    if i == 0:
                        # Keep first Ibn Kaṯīr but change reading to "lā"
                        variants[idx]['words'] = {'1': 'lā', '2': 'ʾuqsimu', '3': 'bi-yaumi', '4': 'l-qiyāmati'}
                    else:
                        # Remove duplicate
                        to_remove.append(idx)
                elif reader == 'Qunbul':
                    # Qunbul also reads "lā" like everyone else
                    variants[idx]['words'] = {'1': 'lā', '2': 'ʾuqsimu', '3': 'bi-yaumi', '4': 'l-qiyāmati'}
            
            # Remove in reverse order
            for idx in sorted(to_remove, reverse=True):
                variants.pop(idx)
            
            # Rebuild indices
            taisir_indices = [i for i, v in enumerate(variants) 
                             if v.get('work') == 'ad-Dānī (gest. 1053): at-Taisīr']
        else:
            # Fix 1: Remove duplicate consecutive reciter entries (general case)
            to_remove = []
            for i in range(len(taisir_indices) - 1):
                idx = taisir_indices[i]
                next_idx = taisir_indices[i + 1]
                
                reader = variants[idx].get('reader', '')
                next_reader = variants[next_idx].get('reader', '')
                
                # If both are numbered reciters and identical, mark for removal
                if (reader and reader[0].isdigit() and 
                    next_reader and next_reader[0].isdigit() and 
                    reader == next_reader):
                    to_remove.append(next_idx)
            
            # Remove duplicates (in reverse to preserve indices)
            for idx in sorted(to_remove, reverse=True):
                variants.pop(idx)
            
            # Rebuild taisir_indices after removal
            taisir_indices = [i for i, v in enumerate(variants) 
                             if v.get('work') == 'ad-Dānī (gest. 1053): at-Taisīr']
        
        # Fix 2: Link transmitters to their reciters
        # Store original reader names to avoid nested parentheses
        original_readers = {idx: variants[idx].get('reader', '') for idx in taisir_indices}
        
        for idx in taisir_indices:
            variant = variants[idx]
            reader = original_readers[idx]
            
            # If it's a transmitter (not numbered), link to preceding reciter
            if reader and not reader[0].isdigit():
                # Find preceding numbered reciter using original names
                for prev_idx in range(idx - 1, -1, -1):
                    if prev_idx in original_readers:
                        prev_reader = original_readers[prev_idx]
                        if prev_reader and prev_reader[0].isdigit():
                            variant['reader'] = f"{prev_reader} ({reader})"
                            break
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Fixed data saved to {output_file}")


if __name__ == "__main__":
    fix_variants()
