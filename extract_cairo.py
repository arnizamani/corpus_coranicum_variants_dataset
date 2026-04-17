#!/usr/bin/env python3
"""Extract Cairo 1924 Quran transliteration from Corpus Coranicum TEI XML."""

import json
import xml.etree.ElementTree as ET
from pathlib import Path


def extract_cairo_transliteration():
    """Extract transliteration and Arabic text from Cairo Quran XML."""
    xml_path = Path(__file__).parent.parent / "corpus-coranicum-tei/data/cairo_quran/cairoquran.xml"
    output_path = Path(__file__).parent / "cairo_quran.json"
    
    if not xml_path.exists():
        print(f"Error: Cairo XML not found at {xml_path}")
        return
    
    print(f"Parsing Cairo Quran XML from {xml_path}...")
    tree = ET.parse(xml_path)
    root = tree.getroot()
    ns = {
        'tei': 'http://www.tei-c.org/ns/1.0',
        'xml': 'http://www.w3.org/XML/1998/namespace'
    }
    
    verses = []
    
    # Extract Arabic text
    print("Extracting Arabic text...")
    arabic_verses = {}
    for verse in root.findall('.//tei:lg', ns):
        verse_id = verse.get('{http://www.w3.org/XML/1998/namespace}id')
        if not verse_id or not verse_id.startswith('verse-'):
            continue
        if verse_id.startswith('transcribed-verse-'):
            continue
        
        parts = verse_id.replace('verse-', '').split('-')
        surah, verse_num = int(parts[0]), int(parts[1])
        
        words = {}
        for w in verse.findall('.//tei:w', ns):
            w_id = w.get('{http://www.w3.org/XML/1998/namespace}id')
            if w_id and w_id.startswith('w-'):
                word_pos = int(w_id.split('-')[-1])
                words[str(word_pos)] = w.text.strip() if w.text else ''
        
        arabic_verses[(surah, verse_num)] = words
    
    # Extract transliteration
    print("Extracting transliteration...")
    for verse in root.findall('.//tei:lg', ns):
        verse_id = verse.get('{http://www.w3.org/XML/1998/namespace}id')
        if not verse_id or not verse_id.startswith('transcribed-verse-'):
            continue
        
        parts = verse_id.replace('transcribed-verse-', '').split('-')
        surah, verse_num = int(parts[0]), int(parts[1])
        
        trans_words = {}
        for w in verse.findall('.//tei:w[@type="word_cc"]', ns):
            w_id = w.get('{http://www.w3.org/XML/1998/namespace}id')
            if w_id and w_id.startswith('transcribed-w-'):
                word_pos = int(w_id.split('-')[-1])
                trans_words[str(word_pos)] = w.text.strip() if w.text else ''
        
        # Combine with Arabic
        arabic_words = arabic_verses.get((surah, verse_num), {})
        
        verses.append({
            'surah': surah,
            'verse': verse_num,
            'words': [
                {
                    'position': int(pos),
                    'transliteration': trans_words.get(pos, ''),
                    'arabic': arabic_words.get(pos, '')
                }
                for pos in sorted(trans_words.keys(), key=int)
            ]
        })
    
    # Sort by surah and verse
    verses.sort(key=lambda v: (v['surah'], v['verse']))
    
    # Save to JSON
    output_data = {
        'source': 'Cairo 1924 Quran (Corpus Coranicum TEI XML)',
        'edition': 'King Fuʾād edition, Amīrī Press, Būlāq (Cairo), 1924',
        'reading': 'Ḥafṣ ʿan ʿĀṣim',
        'orthography': 'rasm ʿuṯmānī (Uthmanic script)',
        'total_verses': len(verses),
        'verses': verses
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Extracted {len(verses)} verses")
    print(f"✓ Saved to {output_path}")
    
    # Calculate size
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"✓ File size: {size_mb:.1f} MB")


if __name__ == "__main__":
    extract_cairo_transliteration()
