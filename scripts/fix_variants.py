#!/usr/bin/env python3
"""Fix issues in all_variants.json downloaded from Corpus Coranicum.

This script fixes several data quality issues:
1. Links transmitters to their reciters (e.g., "ad-Dūrī" -> "3 Abū ʿAmr (ad-Dūrī)")
2. Removes duplicate reciter entries that cause incorrect transmitter linking
3. Fixes 75:1 where only al-Bazzī differs (reads both "la-" and "lā"), not Ibn Kaṯīr
4. Fixes 2:185 where Šuʿba's 'wa-li-tukammilu' is mis-positioned at word 35 (should be 36)
5. Fixes 89:16 where Ibn ʿĀmir's 'fa-qaddara' variant is missing at word 5
6. Fixes 81:10 where 'nuššarat' variant is missing for 4 readers at word 3
7. Fixes 14:19 where 'wa-l-ʾarḍi' variant (Ḥamza, al-Kisāʾī) is missing at word 7
8. Fixes 12:110 where 'fa-nunǧī' readers are wrong at word 11
9. Fixes 11:20 where 'yuḍaʿʿafu' variant (Ibn Kaṯīr, Ibn ʿĀmir) is missing at word 15
"""

import json
from pathlib import Path


# Ad-hoc word-position corrections for known Corpus Coranicum off-by-one errors.
# Format: (surah, verse, reader_substring, {wrong_pos: correct_pos})
POSITION_FIXES = [
    (2, 185, 'ʿĀṣim', {'35': '36'}),  # 'wa-li-tukammilu' is at word 36, not 35
]

# Ad-hoc variant-word overrides for readers where Corpus Coranicum is missing/wrong.
# Format: (surah, verse, reader_exact, {pos: correct_word})
WORD_OVERRIDES = [
    (89, 16, '4 Ibn ʿĀmir', {'5': 'fa-qaddara'}),  # Ibn ʿĀmir reads fa-qaddara, not fa-qadara
    (81, 10, '2 Ibn Kaṯīr', {'3': 'nuššarat'}),   # Ibn Kaṯīr reads nuššarat, not nuširat
    (81, 10, '3 Abū ʿAmr', {'3': 'nuššarat'}),    # Abū ʿAmr reads nuššarat
    (81, 10, '6 Ḥamza', {'3': 'nuššarat'}),       # Ḥamza reads nuššarat
    (81, 10, '7 al-Kisāʾī', {'3': 'nuššarat'}),   # al-Kisāʾī reads nuššarat
    (14, 19, '6 Ḥamza', {'7': 'wa-l-ʾarḍi'}),     # Ḥamza reads wa-l-ʾarḍi (genitive), not wa-l-ʾarḍa
    (14, 19, '7 al-Kisāʾī', {'7': 'wa-l-ʾarḍi'}), # al-Kisāʾī reads wa-l-ʾarḍi (genitive)
    (11, 20, '2 Ibn Kaṯīr', {'15': 'yuḍaʿʿafu'}), # Ibn Kaṯīr reads yuḍaʿʿafu, not yuḍāʿafu
    (11, 20, '4 Ibn ʿĀmir', {'15': 'yuḍaʿʿafu'}), # Ibn ʿĀmir reads yuḍaʿʿafu
]

# Reader-list replacements: at (surah, verse, pos), these are the exact readers reading `word`.
# Applied after WORD_OVERRIDES. Readers not in the list have the entry at `pos` removed
# (meaning they agree with the Hafs reference).
# Format: (surah, verse, pos, word, [exact_reader_names])
READER_LIST_OVERRIDES = [
    (12, 110, '11', 'fa-nunǧī',
     ['1 Nāfiʿ', '2 Ibn Kaṯīr', '3 Abū ʿAmr', '6 Ḥamza', '7 al-Kisāʾī']),
]


def apply_position_fixes(data):
    for verse in data:
        for fix_surah, fix_verse, reader_sub, pos_map in POSITION_FIXES:
            if verse.get('surah') != fix_surah or verse.get('verse') != fix_verse:
                continue
            for variant in verse.get('variants', []):
                if variant.get('work') != 'ad-Dānī (gest. 1053): at-Taisīr':
                    continue
                if reader_sub not in (variant.get('reader') or ''):
                    continue
                words = variant.get('words', {})
                variant['words'] = {pos_map.get(k, k): w for k, w in words.items()}


def apply_word_overrides(data):
    for verse in data:
        for fix_surah, fix_verse, reader_exact, word_map in WORD_OVERRIDES:
            if verse.get('surah') != fix_surah or verse.get('verse') != fix_verse:
                continue
            for variant in verse.get('variants', []):
                if variant.get('work') != 'ad-Dānī (gest. 1053): at-Taisīr':
                    continue
                if (variant.get('reader') or '') != reader_exact:
                    continue
                for pos, word in word_map.items():
                    variant.setdefault('words', {})[pos] = word


def apply_reader_list_overrides(data):
    for verse in data:
        for fix_surah, fix_verse, pos, word, readers in READER_LIST_OVERRIDES:
            if verse.get('surah') != fix_surah or verse.get('verse') != fix_verse:
                continue
            for variant in verse.get('variants', []):
                if variant.get('work') != 'ad-Dānī (gest. 1053): at-Taisīr':
                    continue
                reader = variant.get('reader') or ''
                # Only touch numbered reciter rows (not transmitter rows).
                if not reader or not reader[0].isdigit() or '(' in reader:
                    continue
                words = variant.setdefault('words', {})
                if reader in readers:
                    words[pos] = word
                else:
                    words.pop(pos, None)


def fix_variants():
    input_file = Path(__file__).resolve().parent.parent / "data" / "all_variants.json"
    output_file = Path(__file__).resolve().parent.parent / "data" / "all_variants_fixed.json"
    
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

    apply_position_fixes(data)
    apply_word_overrides(data)
    apply_reader_list_overrides(data)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Fixed data saved to {output_file}")


if __name__ == "__main__":
    fix_variants()
