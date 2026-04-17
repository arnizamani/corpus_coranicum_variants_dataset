#!/usr/bin/env python3
"""Convert all_variants_fixed.json to CSV format with reference text and variants."""

import json
import csv
from pathlib import Path
from collections import defaultdict


def get_reference_text(taisir_variants, surah, verse):
    """Get reference text from empty reader, then Ḥafṣ, then ʿĀṣim, or most complete for special cases."""
    # Special cases: use reader with most consecutive words
    if (surah, verse) in [(10, 87), (19, 72)]:
        best = max(taisir_variants, key=lambda v: len(v.get('words', {})))
        return best.get('words', {})
    
    # Try empty reader first
    for v in taisir_variants:
        if not v.get('reader', '').strip():
            return v.get('words', {})
    
    # Try Ḥafṣ
    for v in taisir_variants:
        if v.get('reader') == '5 ʿĀṣim (Ḥafṣ)':
            return v.get('words', {})
    
    # Try ʿĀṣim
    for v in taisir_variants:
        if v.get('reader') == '5 ʿĀṣim':
            return v.get('words', {})
    
    return {}


def load_cairo_arabic():
    """Load Arabic text from Cairo Quran JSON."""
    json_path = Path(__file__).parent / "cairo_quran.json"
    
    if not json_path.exists():
        print(f"Warning: Cairo Quran data not found at {json_path}")
        return {}
    
    with open(json_path, 'r', encoding='utf-8') as f:
        cairo_data = json.load(f)
    
    arabic_text = {}
    for verse in cairo_data['verses']:
        surah = verse['surah']
        verse_num = verse['verse']
        words = {str(w['position']): w['arabic'] for w in verse['words']}
        arabic_text[(surah, verse_num)] = words
    
    return arabic_text


def convert_to_csv():
    input_file = Path(__file__).parent / "all_variants_fixed.json"
    output_file = Path(__file__).parent / "taisir_variants.csv"
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Load Arabic text
    arabic_text = load_cairo_arabic()
    
    # Define column order
    reciters = ['1 Nāfiʿ', '2 Ibn Kaṯīr', '3 Abū ʿAmr', '4 Ibn ʿĀmir', '5 ʿĀṣim', '6 Ḥamza', '7 al-Kisāʾī']
    transmitters = [
        '1 Nāfiʿ (Qālūn)', '1 Nāfiʿ (Warš)',
        '2 Ibn Kaṯīr (al-Bazzī)', '2 Ibn Kaṯīr (Qunbul)',
        '3 Abū ʿAmr (ad-Dūrī)', '3 Abū ʿAmr (as-Sūsī)',
        '4 Ibn ʿĀmir (Hišām)', '4 Ibn ʿĀmir (Ibn Ḏakwān)',
        '5 ʿĀṣim (Šuʿba)', '5 ʿĀṣim (Ḥafṣ)',
        '6 Ḥamza (Ḫallād)', '6 Ḥamza (Ḫalaf)',
        '7 al-Kisāʾī (ad-Dūrī)', '7 al-Kisāʾī (al-Laiṯ)'
    ]
    
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        
        # Header
        header = ['surah', 'verse', 'word', 'reference', 'reference_cairo'] + reciters + transmitters
        writer.writerow(header)
        
        for verse_data in data:
            surah = verse_data['surah']
            verse = verse_data['verse']
            
            taisir_variants = [v for v in verse_data.get('variants', []) 
                              if v.get('work') == 'ad-Dānī (gest. 1053): at-Taisīr']
            
            if not taisir_variants:
                continue
            
            # Get reference text
            reference = get_reference_text(taisir_variants, surah, verse)
            if not reference:
                continue
            
            # Build variant map: reader -> {word_num: word}
            variant_map = {}
            for v in taisir_variants:
                reader = v.get('reader', '').strip()
                if reader:  # Skip empty reader (it's the reference)
                    variant_map[reader] = v.get('words', {})
            
            # Get Arabic text for this verse
            arabic_words = arabic_text.get((surah, verse), {})
            
            # Process each word in reference
            for word_num in sorted(reference.keys(), key=int):
                ref_word = reference[word_num]
                arabic_word = arabic_words.get(word_num, '')
                row = [surah, verse, word_num, ref_word, arabic_word]
                
                # For each reciter
                for reciter in reciters:
                    reciter_words = variant_map.get(reciter, {})
                    reciter_word = reciter_words.get(word_num, '')
                    
                    # Get transmitter words for this reciter
                    transmitter_prefix = reciter.split()[0] + ' ' + reciter.split()[1]
                    reciter_transmitters = [t for t in transmitters if t.startswith(transmitter_prefix)]
                    
                    trans_words = []
                    for trans in reciter_transmitters:
                        tw = variant_map.get(trans, {}).get(word_num, '')
                        trans_words.append(tw)
                    
                    # If both transmitters agree and differ from reference, use reciter cell
                    # If transmitters disagree or have variants, leave reciter empty
                    if trans_words[0] and trans_words[1] and trans_words[0] == trans_words[1]:
                        # Both transmitters agree
                        if trans_words[0] != ref_word:
                            row.append(trans_words[0])
                        else:
                            row.append('')
                    elif reciter_word and reciter_word != ref_word:
                        # Use reciter word if available and different
                        row.append(reciter_word)
                    else:
                        row.append('')
                
                # For each transmitter
                for transmitter in transmitters:
                    trans_word = variant_map.get(transmitter, {}).get(word_num, '')
                    
                    # Get reciter for this transmitter
                    reciter_prefix = ' '.join(transmitter.split()[:2])
                    
                    # Get both transmitters for this reciter
                    reciter_transmitters = [t for t in transmitters if t.startswith(reciter_prefix)]
                    trans_words = [variant_map.get(t, {}).get(word_num, '') for t in reciter_transmitters]
                    
                    # Only fill if transmitters disagree or have variants
                    if trans_words[0] != trans_words[1] or '/' in (trans_word or ''):
                        if trans_word and trans_word != ref_word:
                            row.append(trans_word)
                        else:
                            row.append('')
                    else:
                        row.append('')
                
                writer.writerow(row)
    
    print(f"Converted to {output_file}")


if __name__ == "__main__":
    convert_to_csv()
