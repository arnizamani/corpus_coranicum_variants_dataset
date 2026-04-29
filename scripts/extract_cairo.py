#!/usr/bin/env python3
"""Extract Cairo 1924 Quran transliteration from Corpus Coranicum TEI XML."""

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

SHADDA = '\u0651'
# Short harakāt and tanwīn marks that the Cairo XML places *before* shadda.
# Unicode recommends the inverse: shadda first, then the haraka.
_HARAKAT_BEFORE_SHADDA = ('\u064E', '\u064F', '\u0650', '\u064B', '\u064C', '\u064D')  # fatha/damma/kasra + tanwīns

# Precomposed alef-with-madda-above → alef + combining maddah-above. Decomposed
# form matches the Madinah mushaf's representation and keeps the base letter
# visible as a plain alef.
ALEF_MADDA = '\u0622'
ALEF_PLUS_MADDAH = '\u0627\u0653'

# Cairo uses U+06E4 (small high madda, a Quranic annotation glyph) in places
# where the standard combining madda U+0653 is the appropriate Unicode code
# point. Collapse the former to the latter.
SMALL_HIGH_MADDA = '\u06E4'
MADDAH_ABOVE = '\u0653'

# Cairo uses U+0674 (ARABIC LETTER HIGH HAMZA) as a standalone glyph where
# Madinah uses the combining pair U+0640 U+0654 (tatweel + hamza-above). The
# hamza-above then combines with the following haraka as usual.
HIGH_HAMZA = '\u0674'
TATWEEL = '\u0640'
HAMZA_ABOVE = '\u0654'
SUPERSCRIPT_ALEF = '\u0670'

# Combining-mark reorder: Cairo places hamza-above *after* a following tanwīn
# (e.g. U+08F0 U+0654), but the natural reading order — and Madinah's
# representation — has hamza-above first, tanwīn second. Cover both the
# regular fathatan and the open-fathatan form (the other tanwīn flavours do
# not co-occur with hamza-above in the corpus).
_TANWIN_AFTER_HAMZA_ABOVE = ('\u08F0', '\u064B')

# Similarly, Cairo places fatha / damma after a following hamza-above rather
# than before; Madinah puts hamza-above first (the hamza is part of the base
# consonant, the vowel sits on top of it).
# Small high marks that annotate the base consonant (alternative-reading
# indicators like small-high-seen). Madinah places them before the vowel; if
# Cairo has the vowel first, swap so the consonant-annotation comes first.
_CONSONANT_ANNOTATIONS = ('\u06DC',)  # small high seen
_SHORT_VOWELS_BEFORE_HAMZA_ABOVE = ('\u064E', '\u064F')  # fatha, damma

# When Cairo has kasra + hamza-above, the hamza is actually rendered *below*
# the baseline (the kasra attracts it). Rewrite to hamza-below + kasra, the
# form used throughout the project (see hafs/postformat.py line 100).

# Move hamza below the baseline when followed by kasra. This matches the
# convention used elsewhere in the project (see hafs/postformat.py
# `move_hamza_kasra_below_baseline`): U+0626 (yeh-hamza-above) + kasra
# becomes U+0649 (alef maksura) + hamza-below + kasra. We also reorder the
# pre-existing decomposed form U+0649 + kasra + hamza-below into the same
# canonical hamza-below-first ordering.
YEH_HAMZA_ABOVE = '\u0626'
ALEF_MAKSURA = '\u0649'
KASRA = '\u0650'
HAMZA_BELOW = '\u0655'
FARSI_YEH = '\u06CC'
ARABIC_YEH = '\u064A'

# Cairo 1924 annotates tanwīn-sandhi with small-meem glyphs — the position
# (high / low) depends on the vowel:
#
#   fathatan + low-meem  (U+064B U+06ED) → open fathatan  (idghām / ikhfāʾ)
#   fathatan + high-meem (U+064B U+06E2) → iqlāb fathatan (before bāʾ)
#
#   dammatan + low-meem  (U+064C U+06ED) → open dammatan
#   dammatan + high-meem (U+064C U+06E2) → iqlāb dammatan
#
#   kasratan + high-meem (U+064D U+06E2) → open kasratan (!)
#   kasratan + low-meem  (U+064D U+06ED) → iqlāb kasratan (!)
#
# Kasratan uses the *opposite* meem-position compared with fathatan and
# dammatan — verified empirically against the raw XML (iqlāb positions are
# tanwīn-before-bāʾ). Open-tanwīn forms collapse to Extended-Arabic-A
# U+08F0/U+08F1/U+08F2. Iqlāb forms collapse to `haraka + U+06E2`, matching
# Madinah's iqlāb encoding. Open and iqlāb are kept strictly distinct.
_TANWIN_SANDHI_OPEN = {
    '\u064B\u06ED': '\u08F0',  # fathatan + low-meem  → open fathatan
    '\u064C\u06ED': '\u08F1',  # dammatan + low-meem  → open dammatan
    '\u064D\u06E2': '\u08F2',  # kasratan + high-meem → open kasratan
}
_TANWIN_IQLAB = {
    '\u064B\u06E2': '\u064E\u06E2',  # fathatan + high-meem → fatha + high-meem
    '\u064C\u06E2': '\u064F\u06E2',  # dammatan + high-meem → damma + high-meem
    '\u064D\u06ED': '\u0650\u06ED',  # kasratan + low-meem  → kasra + low-meem (matches Madinah)
}

# When alef-maksura (U+0649) carries a haraka, tanwīn, shadda, sukūn sign, or
# open-tanwīn, it is acting as a *consonant* (phonetically a yāʾ) rather than
# a long-vowel carrier. In that case the intended letter is Arabic yeh, but
# writing U+064A would reintroduce the two dots; the project uses Farsi yeh
# (U+06CC) instead to suppress them in the final form. The (U+0649 U+0655 …)
# pattern is intentionally excluded — there the maksura is a hamza seat.
_MAKSURA_CONSONANT_TRIGGERS = (
    '\u064B', '\u064C', '\u064D',           # tanwīn fath/damm/kasr
    '\u064E', '\u064F', '\u0650',           # fatha, damma, kasra
    '\u0651', '\u0652', '\u06E1',           # shadda, sukūn, small high sukūn
    '\u0653',                                # maddah-above
    '\u08F0', '\u08F1', '\u08F2',           # open fathatan/dammatan/kasratan
)

# Canonical waqf (pause) signs used by the mushaf. Must match the parent-repo
# list in src/common/constants.py (WAQF_SIGNS).
WAQF_SIGNS = ('\u06D6', '\u06D7', '\u06D8', '\u06D9', '\u06DA', '\u06DB')
SAJDA = '\u06E9'  # prostration sign, also not part of the core word text
# Trailing vowel-extension glyphs that sometimes appear *after* a waqf sign
# in the XML. Logically the waqf belongs at the word-end; these short suffixes
# get moved past it during splitting so the waqf goes into its own field.
_TRAILING_VOWEL_EXTENSIONS = ('\u06E5', '\u06E6', '\u06E6\u0653')  # small-high waw / yeh / yeh+madda


def _split_trailing(text: str, marks):
    """Return (core, mark). If `text` ends in one of `marks` (possibly before
    a trailing vowel-extension glyph like U+06E5, U+06E6, or U+06E6 U+0653),
    split it off."""
    if not text:
        return text, ''
    if text[-1] in marks:
        return text[:-1], text[-1]
    for ext in _TRAILING_VOWEL_EXTENSIONS:
        n = len(ext)
        if len(text) > n and text[-n:] == ext and text[-(n+1)] in marks:
            return text[:-(n+1)] + ext, text[-(n+1)]
    return text, ''


def _make_word(position: int, transliteration: str, arabic: str) -> dict:
    """Build a word dict, splitting trailing waqf and sajda signs into their
    own fields."""
    core, waqf = _split_trailing(arabic, WAQF_SIGNS)
    core, sajda = _split_trailing(core, (SAJDA,))
    word = {'position': position, 'transliteration': transliteration, 'arabic': core}
    if waqf:
        word['waqf_ending'] = waqf
    if sajda:
        word['sajda_ending'] = sajda
    # After normalization and splitting, the core Arabic word must not contain
    # any waqf (pause) sign; those belong in `waqf_ending` only.
    assert not any(ch in WAQF_SIGNS for ch in core), (
        f'waqf sign survived in core word at position {position}: '
        f'{core!r} (code points: {[f"U+{ord(c):04X}" for c in core]})'
    )
    return word


_DATA_DIR = Path(__file__).resolve().parent.parent / 'data'
_SAJDA_POSITIONS_PATH = _DATA_DIR / 'cairo_patches' / 'sajda_positions.json'
_WORD_BOUNDARY_FIXES_PATH = _DATA_DIR / 'cairo_patches' / 'word_boundary_fixes.json'
_WORD_CONTENT_FIXES_PATH = _DATA_DIR / 'cairo_patches' / 'word_content_fixes.json'


def _attach_sajda_signs(verses):
    """Mark the last word of each sajda verse with sajda_ending=U+06E9."""
    with open(_SAJDA_POSITIONS_PATH, encoding='utf-8') as f:
        positions = {(p['surah'], p['verse']) for p in json.load(f)}
    index = {(v['surah'], v['verse']): v for v in verses}
    for key in positions:
        verse = index.get(key)
        assert verse and verse['words'], f'sajda position {key} not found'
        verse['words'][-1]['sajda_ending'] = SAJDA


def _apply_word_boundary_fixes(verses):
    """Rewrite specific mis-split / transposed word pairs in the Cairo XML.
    Each fix is validated by checking that the multiset of characters across
    the affected words is preserved (so no text is added or lost); if not,
    the fix is stale and requires human review."""
    with open(_WORD_BOUNDARY_FIXES_PATH, encoding='utf-8') as f:
        fixes = json.load(f)
    index = {(v['surah'], v['verse']): v for v in verses}
    for fix in fixes:
        verse = index.get((fix['surah'], fix['verse']))
        assert verse, f'word boundary fix references missing verse {fix}'
        words = verse['words']
        pos_to_word = {w['position']: w for w in words}
        targets = [pos_to_word[p] for p in fix['word_positions']]
        old_ar = sorted(''.join(w['arabic'] for w in targets))
        new_ar = sorted(''.join(fix['arabic']))
        assert old_ar == new_ar, (
            f'word boundary fix invalid (arabic char multiset mismatch) at '
            f'{fix["surah"]}:{fix["verse"]}: '
            f'old={"".join(w["arabic"] for w in targets)!r} '
            f'new={"".join(fix["arabic"])!r}'
        )
        old_tr = sorted(''.join(w.get('transliteration', '') for w in targets))
        new_tr = sorted(''.join(fix['transliteration']))
        assert old_tr == new_tr, (
            f'word boundary fix invalid (translit char multiset mismatch) at '
            f'{fix["surah"]}:{fix["verse"]}'
        )
        for w, new_ar_word, new_tr_word in zip(targets, fix['arabic'], fix['transliteration']):
            w['arabic'] = new_ar_word
            w['transliteration'] = new_tr_word


def _apply_word_content_fixes(verses):
    """Overwrite individual words whose Cairo XML content diverges from the
    printed Cairo 1924 mushaf (e.g. a missing shadda). Each fix must name the
    exact current arabic/transliteration so stale entries fail loudly."""
    with open(_WORD_CONTENT_FIXES_PATH, encoding='utf-8') as f:
        fixes = json.load(f)
    index = {(v['surah'], v['verse']): v for v in verses}
    for fix in fixes:
        verse = index.get((fix['surah'], fix['verse']))
        assert verse, f'word content fix references missing verse {fix}'
        word = next((w for w in verse['words'] if w['position'] == fix['word_position']), None)
        assert word is not None, f'word content fix: position {fix["word_position"]} not found at {fix["surah"]}:{fix["verse"]}'
        assert word['arabic'] == fix['arabic_old'], (
            f'word content fix stale (arabic) at {fix["surah"]}:{fix["verse"]} '
            f'pos {fix["word_position"]}: expected {fix["arabic_old"]!r}, got {word["arabic"]!r}'
        )
        assert word.get('transliteration', '') == fix['transliteration_old'], (
            f'word content fix stale (translit) at {fix["surah"]}:{fix["verse"]} '
            f'pos {fix["word_position"]}'
        )
        word['arabic'] = fix['arabic_new']
        word['transliteration'] = fix['transliteration_new']


def normalize_arabic(text: str) -> str:
    """Make Arabic text Unicode-compliant. Currently:
    - swap haraka+shadda to shadda+haraka so shadda precedes its vowel;
    - decompose U+0622 (ʾalif-madda) into U+0627 U+0653 (alef + maddah-above);
    - collapse U+06E4 (small high madda) to U+0653 (standard madda);
    - replace U+0674 (high hamza) with U+0640 U+0654 (tatweel + hamza-above);
    - reorder tanwīn+hamza-above to hamza-above+tanwīn (U+08F0/U+064B after
      U+0654);
    - reorder fatha/damma + hamza-above to hamza-above + fatha/damma;
    - rewrite kasra + hamza-above to hamza-below + kasra (Madinah convention
      for hamza-on-kasra, matching hafs/postformat.py);
    - move hamza below baseline when followed by kasra (yeh-hamza+kasra →
      alef-maksura + hamza-below + kasra), and reorder the alternate
      decomposed form to match;
    - collapse tanwīn + small-meem (U+06ED/U+06E2) to the corresponding
      open-tanwīn code point (U+08F0/U+08F1/U+08F2);
    - rewrite alef-maksura → Farsi yeh when it carries a haraka/shadda/sukūn
      (i.e. acts as a consonant, not a long-vowel carrier).
    """
    # Source glitch at Saba' 34:8 — a waqf sign (U+06D7) is placed before the
    # final letter of `جِنَّةٌۢ`. Restore the expected order (waqf at word-end).
    text = text.replace('\u0651\u06D7\u0629\u064C\u06E2', '\u0651\u0629\u064C\u06E2\u06D7')
    # Madinah uses Farsi yeh (U+06CC) uniformly; Cairo uses Arabic yeh
    # (U+064A). Collapse Cairo to match — this applies to both consonantal
    # yāʾ (carrying marks) and long-vowel yāʾ (plain letter in the middle or
    # start of a word).
    text = text.replace(ARABIC_YEH, FARSI_YEH)
    # Source glitches: a handful of words carry an ASCII space in the middle
    # or use the plain sukūn (U+0652) instead of the project-wide small-high
    # sukūn (U+06E1). Repair both.
    text = text.replace(' ', '')
    text = text.replace('\u0652', '\u06E1')
    # Source glitch at Baqarah 2:72 — `فَٱدَّٰرءۡتُمۡ` is missing the fatha
    # between ر and the following hamza letter (applies after the generic
    # space-removal and sukūn fixes normalize the surrounding marks).
    text = text.replace('\u0670\u0631\u0621\u06E1', '\u0670\u0631\u064E\u0621\u06E1')
    for h in _HARAKAT_BEFORE_SHADDA:
        text = text.replace(h + SHADDA, SHADDA + h)
    text = text.replace(ALEF_MADDA, ALEF_PLUS_MADDAH)
    text = text.replace(SMALL_HIGH_MADDA, MADDAH_ABOVE)
    text = text.replace(HIGH_HAMZA, TATWEEL + HAMZA_ABOVE)
    text = text.replace(YEH_HAMZA_ABOVE + KASRA, ALEF_MAKSURA + HAMZA_BELOW + KASRA)
    text = text.replace(ALEF_MAKSURA + KASRA + HAMZA_BELOW, ALEF_MAKSURA + HAMZA_BELOW + KASRA)
    for src, dst in _TANWIN_SANDHI_OPEN.items():
        text = text.replace(src, dst)
        # Also handle the rare source ordering `tanwīn + hamza-above + meem`
        # (e.g. هَنِيٓـًٔۢا). The pair after hamza-above still collapses to
        # the open-tanwīn code point.
        tanwin = src[0]
        marker = src[1]
        text = text.replace(tanwin + HAMZA_ABOVE + marker, HAMZA_ABOVE + dst)
    for src, dst in _TANWIN_IQLAB.items():
        text = text.replace(src, dst)
        tanwin = src[0]
        marker = src[1]
        text = text.replace(tanwin + HAMZA_ABOVE + marker, HAMZA_ABOVE + dst)
    # Yeh-hamza-above followed by open kasratan is a kasr-tanwīn position:
    # the hamza is actually below the baseline. Rewrite to
    # Farsi-yeh + hamza-below + open-kasratan (no dots on the base, hamza
    # precedes the vowel per canonical combining order).
    text = text.replace(YEH_HAMZA_ABOVE + '\u08F2', FARSI_YEH + HAMZA_BELOW + '\u08F2')
    for t in _TANWIN_AFTER_HAMZA_ABOVE:
        text = text.replace(t + HAMZA_ABOVE, HAMZA_ABOVE + t)
    for v in _SHORT_VOWELS_BEFORE_HAMZA_ABOVE:
        text = text.replace(v + HAMZA_ABOVE, HAMZA_ABOVE + v)
        for annotation in _CONSONANT_ANNOTATIONS:
            text = text.replace(v + annotation, annotation + v)
        # Same reorder when a superscript alef sits between the vowel and the
        # hamza (e.g. `fatha + sup-alef + hamza-above` → `hamza-above + fatha
        # + sup-alef`). Canonical order: hamza first, then vowel, then
        # length-extension mark.
        text = text.replace(v + SUPERSCRIPT_ALEF + HAMZA_ABOVE,
                            HAMZA_ABOVE + v + SUPERSCRIPT_ALEF)
    text = text.replace(KASRA + HAMZA_ABOVE, HAMZA_BELOW + KASRA)
    for trigger in _MAKSURA_CONSONANT_TRIGGERS:
        text = text.replace(ALEF_MAKSURA + trigger, FARSI_YEH + trigger)
    # Alef-maksura preceded by kasra and *not* followed by a hamza-below is a
    # consonantal yāʾ (e.g. أَخِى → أَخِي), so rewrite to Farsi yeh.
    text = re.sub(KASRA + ALEF_MAKSURA + r'(?!' + HAMZA_BELOW + r')', KASRA + FARSI_YEH, text)
    # Superscript alef must sit over a fatha, except when it acts as the long-
    # vowel mark on an alef-maksura (U+0649) or waw (U+0648) carrier. Insert a
    # fatha whenever U+0670 follows any other base letter. This also repairs
    # the `يٰٓأُو۟...` words where the fatha on the initial yāʾ is missing.
    text = re.sub(r'(?<![\u064E\u0648\u0649])\u0670', '\u064E\u0670', text)
    return text


def extract_cairo_transliteration():
    """Extract transliteration and Arabic text from Cairo Quran XML."""
    xml_path = Path(__file__).resolve().parent.parent.parent / "corpus-coranicum-tei/data/cairo_quran/cairoquran.xml"
    output_path = _DATA_DIR / "cairo_quran.json"
    
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
                words[str(word_pos)] = normalize_arabic(w.text.strip()) if w.text else ''
        
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
                _make_word(int(pos), trans_words.get(pos, ''), arabic_words.get(pos, ''))
                for pos in sorted(trans_words.keys(), key=int)
            ]
        })
    
    # Sort by surah and verse
    verses.sort(key=lambda v: (v['surah'], v['verse']))

    # Repair known mis-split word boundaries (see word_boundary_fixes.json).
    _apply_word_boundary_fixes(verses)

    # Repair known per-word content errors in the Cairo XML that disagree
    # with the printed Cairo 1924 mushaf (see word_content_fixes.json).
    _apply_word_content_fixes(verses)

    # Attach sajda signs to the final word of each sajda verse. Positions are
    # tracked in a small bundled dataset (see sajda_positions.json) so the
    # submodule stays self-contained.
    _attach_sajda_signs(verses)
    
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
