# Data Documentation

## Dataset Overview

This dataset contains word-by-word Quranic variant readings for the seven canonical reciters according to ad-Dānī's *at-Taisīr fī l-qirāʾāt as-sabʿ*.

## Files

### Repository Layout

```
corpus_coranicum_variants_dataset/
├── data/                                # published data artefacts
│   ├── all_variants_fixed.json         # ~25 MB — complete dataset, all sources, quality-fixed
│   ├── taisir_variants.csv             # ~4.5 MB — at-Taisīr variants only (primary published CSV)
│   ├── cairo_quran.json                # ~10 MB — Cairo 1924 reference, verified + normalised
│   ├── ayah_numbering_variants.csv     # ~11 KB — verse-ending variants across 6 counting systems
│   └── cairo_patches/                  # small datasets consumed by extract_cairo.py
│       ├── sajda_positions.json
│       ├── word_boundary_fixes.json
│       └── word_content_fixes.json
├── scripts/                             # Python / JS pipeline
│   ├── scrape.js, fix_variants.py,
│   │   convert_to_csv.py, convert_ayah_variants.py,
│   │   extract_cairo.py,
│   │   transliterate_to_arabic.py,
│   │   normalize_arabic.py
│   └── debug/                          # one-off diagnostic helpers
├── tests/                               # pytest tests + regression fixtures
└── docs/                                # project documentation
```

### Core Data Files

| File | Size | Format | Description |
|------|------|--------|-------------|
| `data/all_variants_fixed.json` | ~25 MB | JSON | Complete dataset with all sources and quality fixes applied |
| `data/taisir_variants.csv` | ~4.5 MB | CSV | Tabular format with **only ad-Dānī's at-Taisīr variants** |
| `data/cairo_quran.json` | ~10 MB | JSON | Cairo 1924 Quran reference text (Ḥafṣ reading), verified against the Madinah mushaf and normalised — see [Cairo Reference Text Curation](#cairo-reference-text-curation) below |
| `data/ayah_numbering_variants.csv` | ~11 KB | CSV | Verse ending variants across six classical counting systems |

**Note**: `data/all_variants.json` (raw scraped data) is not published as it's an intermediate file. Use `all_variants_fixed.json` instead.

**Self-Contained**: All data files are included in this repository. No external dependencies on Corpus Coranicum TEI XML files are needed at runtime; `scripts/extract_cairo.py` does require the TEI XML as input but only when regenerating `cairo_quran.json` from scratch.

### Code Files

| File | Language | Purpose |
|------|----------|---------|
| `scripts/scrape.js` | JavaScript | Main scraper (uses Playwright) |
| `scripts/fix_variants.py` | Python | Data quality fixes for variant readings |
| `scripts/convert_to_csv.py` | Python | JSON to CSV converter |
| `scripts/convert_ayah_variants.py` | Python | Builds `data/ayah_numbering_variants.csv` |
| `scripts/extract_cairo.py` | Python | Extract and normalise the Cairo 1924 text from TEI XML |
| `scripts/transliterate_to_arabic.py` | Python | Transliteration → Arabic helper (used by tests) |
| `scripts/normalize_arabic.py` | Python | Arabic Unicode normaliser (helper) |
| `data/cairo_patches/sajda_positions.json` | JSON | 15 (surah, verse) positions where `۩` is attached after extraction |
| `data/cairo_patches/word_boundary_fixes.json` | JSON | Per-verse repairs for words the upstream XML mis-split |
| `data/cairo_patches/word_content_fixes.json` | JSON | Per-word rewrites where the XML source diverged from the printed Cairo 1924 mushaf |
| `tests/test_variants.py` | Python | Validation tests (pytest) |
| `scripts/debug/find_multiple_variants.py` | Python | Analysis tool for data quality |

## Data Structure

### JSON Format

Each verse entry in `all_variants_fixed.json` contains:

```json
{
  "surah": 1,
  "verse": 1,
  "variants": [
    {
      "work": "ad-Dānī (gest. 1053): at-Taisīr",
      "reader": "5 ʿĀṣim (Ḥafṣ)",
      "words": {
        "1": "bi-smi",
        "2": "llāhi",
        "3": "r-raḥmāni",
        "4": "r-raḥīmi"
      }
    }
  ],
  "success": true
}
```

#### Field Descriptions

- **surah** (integer): Surah number (1-114)
- **verse** (integer): Verse number within the surah (1-indexed)
- **variants** (array): List of variant readings for this verse
  - **work** (string): Source book with author and death date
  - **reader** (string): Reciter or transmitter name
    - Format for reciters: `"# Name"` (e.g., `"5 ʿĀṣim"`)
    - Format for transmitters: `"# Reciter (Transmitter)"` (e.g., `"5 ʿĀṣim (Ḥafṣ)"`)
  - **words** (object): Word positions and their readings
    - Keys: Word position (string representation of 1-indexed integer)
    - Values: Transliterated word
- **success** (boolean): Whether scraping succeeded for this verse

### CSV Format

The CSV file (`taisir_variants.csv`) contains **only variants from ad-Dānī's at-Taisīr** (the seven canonical readings). Other sources present in the JSON are excluded.

The CSV has the following columns:

#### Identification Columns
1. **surah**: Surah number (1-114)
2. **verse**: Verse number
3. **word**: Word position within the verse (1-indexed)

#### Reference Columns
4. **reference**: Reference text in transliteration (Ḥafṣ reading)
5. **reference_cairo**: Arabic text from Cairo 1924 Quran

#### Reciter Columns (7 columns)
6-12. One column per reciter:
   - `1 Nāfiʿ`
   - `2 Ibn Kaṯīr`
   - `3 Abū ʿAmr`
   - `4 Ibn ʿĀmir`
   - `5 ʿĀṣim`
   - `6 Ḥamza`
   - `7 al-Kisāʾī`

**Filled when**: Both transmitters agree AND differ from reference

#### Transmitter Columns (14 columns)
13-26. Two columns per reciter (one per transmitter):
   - `1 Nāfiʿ (Qālūn)`, `1 Nāfiʿ (Warš)`
   - `2 Ibn Kaṯīr (al-Bazzī)`, `2 Ibn Kaṯīr (Qunbul)`
   - `3 Abū ʿAmr (ad-Dūrī)`, `3 Abū ʿAmr (as-Sūsī)`
   - `4 Ibn ʿĀmir (Hišām)`, `4 Ibn ʿĀmir (Ibn Ḏakwān)`
   - `5 ʿĀṣim (Šuʿba)`, `5 ʿĀṣim (Ḥafṣ)`
   - `6 Ḥamza (Ḫallād)`, `6 Ḥamza (Ḫalaf)`
   - `7 al-Kisāʾī (ad-Dūrī)`, `7 al-Kisāʾī (al-Laiṯ)`

**Filled when**: Transmitters disagree OR have variants

### CSV Logic Example

For a word where:
- Reference (Ḥafṣ): `bi-smi`
- Qālūn: `bi-smi` (same as reference)
- Warš: `bi-smi` (same as reference)

Result: All Nāfiʿ columns are **empty** (no difference from reference)

For a word where:
- Reference (Ḥafṣ): `māliki`
- Qālūn: `maliki` (different)
- Warš: `maliki` (different, same as Qālūn)

Result:
- `1 Nāfiʿ` column: `maliki` (both transmitters agree)
- Transmitter columns: **empty** (no disagreement between transmitters)

For a word where:
- Reference (Ḥafṣ): `yaʿmalūna`
- Šuʿba: `taʿmalūna` (different)
- Ḥafṣ: `yaʿmalūna` (same as reference)

Result:
- `5 ʿĀṣim` column: **empty** (transmitters disagree)
- `5 ʿĀṣim (Šuʿba)` column: `taʿmalūna`
- `5 ʿĀṣim (Ḥafṣ)` column: **empty** (same as reference)

### Verse Numbering Variants Format

The `ayah_numbering_variants.csv` file documents differences in verse division across six classical counting systems.

#### The Six Counting Systems

| System | Total Verses | Authority | Chain of Narration |
|--------|--------------|-----------|-------------------|
| **Kufi** | 6,236 | Hamzah al-Zayyat (d. 156) | From 'Ali ibn Abi Talib (d. 40) |
| **Madani 1** | 6,214 | Nafi' (d. 169) | From Abu Jafar Yazid (d. 128) via Isma'il ibn Jafar |
| **Madani 2** | 6,217 | Nafi' (d. 169) | From Abu Jafar Yazid (d. 128) via Kufi scholars |
| **Makki** | 6,210 | Ibn Kathir (d. 120) | From Mujahid from Ibn 'Abbas from Ubay ibn Ka'b |
| **Basri** | 6,204 | 'Ata ibn Yasar (d. 102) | Via Asim al-Jahdari from Ayub ibn al-Mutawakkil |
| **Shami** | 6,226 | Ibn 'Amir (d. 118) | From Abu al-Darda', attributed to 'Uthman ibn 'Affan |

The Kufi system (6,236 verses) is used as the reference in this dataset and aligns with modern Hafs numbering.

#### Columns

1. **surah**: Surah number (1-114)
2. **verse**: Verse number (Kufi/Hafs reference numbering)
3. **word_position**: Position of the word where the variant occurs
4. **madani1**: Madani al-Awwal system (`+1` = verse break, `-1` = no verse break)
5. **madani2**: Madani al-Akheer system
6. **makki**: Makki system
7. **basari**: Basari system
8. **shami**: Shami system
9. **kufi**: Kufi system (same as reference)

#### Value Meanings

- **+1**: This system considers this location a verse ending
- **-1**: This system does NOT consider this location a verse ending

The Kufi system is used as the reference, which aligns with modern Hafs numbering.

#### Example

```csv
surah,verse,word_position,madani1,madani2,makki,basari,shami,kufi
1,1,4,-1,-1,1,-1,-1,1
```

This means at Surah 1, Verse 1 (Kufi), word position 4:
- Makki and Kufi systems: verse break exists (+1)
- Other systems: no verse break (-1)

Note that the issue of Basmala in Surah al-Fatihah is a special case. For the Makki and Kufi systems, Basmala is the first verse of Surah al-Fatihah, while others do not consider it as a verse of al-Fatihah.

#### Coverage

- **Total variants**: 241 locations
- **Surahs affected**: 74 out of 114
- **Systems**: 6 classical counting traditions

These differences have full coverage of the Quranic text. All other positions of end-of-ayah are in complete agreement between these six systems.

## Cairo Reference Text Curation

The Arabic text in `cairo_quran.json` — and consequently the `reference_cairo`
column in `taisir_variants.csv` — has been verified **word-by-word** against
the hand-verified Madinah mushaf and patched so that every difference is
either a genuine editorial/tajwīd convention or has been resolved. The final
state is zero unresolved character-level differences across all 77 k words.

### What was done

1. **Schema additions.** Per-word annotations that are visually separate
   from the text proper are split into their own JSON fields so the core
   Arabic string is clean:
   - `waqf_ending`: a single pause sign (U+06D6–U+06DB) if the word ends
     with one. `extract_cairo.py` asserts that no waqf sign ever survives
     inside the core `arabic` field.
   - `sajda_ending`: `۩` (U+06E9) for the final word of each of the 15
     sajdat at-tilāwa verses. Positions listed in `sajda_positions.json`.

2. **Cosmetic Unicode-compliance normalisations** (applied uniformly to
   every Cairo word by `extract_cairo.py` — no semantic change):
   - Combining-mark reorder: `haraka + shadda` → `shadda + haraka`, and
     several analogous hamza-above / tanwīn reorderings so combining marks
     follow canonical reading order.
   - `U+0622` (precomposed alef-madda) → `U+0627 U+0653` (alef + combining
     maddah-above), matching Madinah.
   - `U+06E4` (small high madda) → `U+0653` (standard maddah-above).
   - `U+0674` (high-hamza letter) → `U+0640 U+0654` (tatweel + hamza-above).
   - Arabic yeh (`U+064A`) → Farsi yeh (`U+06CC`) throughout, matching
     Madinah's convention of suppressing the two dots on yeh.
   - Alef-maksura (`U+0649`) → Farsi yeh when it carries a haraka / shadda
     / sukūn — i.e. when it acts as a consonant rather than a long-vowel
     carrier. Genuine word-final alef-maksura (e.g. `عَلَىٰ`) is preserved.
   - `yeh-hamza-above + kasra` (`U+0626 U+0650`) → `alef-maksura +
     hamza-below + kasra` (`U+0649 U+0655 U+0650`). Moves the hamza below
     the baseline where the kasra attracts it — same convention as the
     printed Cairo mushaf.
   - Plain sukūn (`U+0652`, 4 occurrences) → small-high-sukūn (`U+06E1`),
     the form used everywhere else.

3. **Tanwīn / iqlāb disambiguation.** The raw XML uses a pair of small
   meem glyphs to annotate tanwīn-sandhi, and the Cairo 1924 edition
   assigns them on a **vowel-sensitive** basis (verified empirically
   against iqlāb-before-bāʾ positions):

   | tanwīn | `+ low-meem (U+06ED)` | `+ high-meem (U+06E2)` |
   |--------|------------------------|------------------------|
   | fathatan | open fathatan | iqlāb fathatan |
   | dammatan | open dammatan | iqlāb dammatan |
   | kasratan | iqlāb kasratan | open kasratan |

   Note the kasratan row uses the *opposite* meem-position compared with
   the other two — this is how the Cairo mushaf itself prints them, and
   the data was verified against iqlāb contexts (tanwīn-before-bāʾ).

   Open-tanwīn pairs collapse to Extended-Arabic-A U+08F0 / U+08F1 /
   U+08F2. Iqlāb pairs collapse to `haraka + meem` (dropping the redundant
   tanwīn), matching Madinah's native iqlāb encoding. **Regular tanwīn and
   open tanwīn are kept strictly distinct throughout** — no fold between
   them exists anywhere in the pipeline.

4. **Source-error corrections against the printed mushaf.** These are cases
   where the Corpus Coranicum XML text diverges from the printed Cairo 1924
   edition, verified by scanning the mushaf page. All are persisted in
   `word_content_fixes.json`; each entry names the exact pre-fix
   `arabic_old` string, so any future normaliser change that alters a
   targeted word trips an assertion and flags the fix for re-verification.
   Categories include:
   - Missing shadda on a preposition lām after an idghām trigger
     (e.g. `قُل لِّأَزْوَاجِكَ` at 33:28, 33:59; `لِّأَزْوَاجِهِم` at
     2:240; `لِّأَنفُسِهِمۡ` at 3:178, 64:16; …).
   - Missing haraka (fatha or kasra) on consonants before a superscript
     alef or at word-end (`یَأۡتِیَ`, `مَعِیَ`, `أَجۡرِیَ`, `ٱلۡعَاجِلَةَ`,
     …).
   - Missing U+06DF silent-char at the end of `كَانُوا۟`-type words.
   - Missing iqlāb / nūn+sukūn marker (e.g. `مِنۢ` at 13:11).
   - Missing trailing fatha on verb endings like `فَأُوَٰرِيَ` (5:31).
   - Shadda placed on the wrong lām in `ٱللَّٰعِنُونَ` (2:159).
   - Boundary mis-splits: `فَٱدَّٰ رءْتُمْ` split in the middle at 2:72;
     `وَكَانُوا / كَانُوا۟` transposed at 21:90; `يَٰٓأُو۟ / لِيٱلۡأَلۡبَٰبِ`
     split at the wrong character at 5:100. Tracked in
     `word_boundary_fixes.json`.

5. **Valid editorial differences kept intact.** A small whitelist of
   genuine mushaf-editorial or tajwīd-convention differences is documented
   in the compare tool and not modified. The dominant class is iqlāb
   handling at surah boundaries:

   - Madinah reads the next surah's bismillah, so the last-word tanwīn is
     annotated as iqlāb against the `ب` of `بِسْمِ`.
   - The Cairo 1924 edition does not repeat the bismillah between surahs
     in the text layout, and consequently annotates the same last word
     with open tanwīn (the pronunciation when reading straight to the
     next surah's first word).

   Other accepted differences include:
   - Small-high-seen alternative-reading annotations on ṣād at Ṭūr 52:37
     and Ghāshiyah 88:22 (Madinah uses U+06DC, Cairo uses U+06E3).
   - Al-Ḥāqqah 69:28–29's sakta annotation (Madinah has a small-high-seen
     sakta marker at the end of `مَالِيَهۡ`; Cairo marks the next word
     `هَلَكَ` with a shadda related to the same sakta convention).
   - Yusuf 12:39, 41 where Cairo keeps a mid-word alef-maksura as a
     sup-alef carrier that Madinah attaches to ص directly.
   - Yusuf 12:11 `تَأۡمَنَّا` ishmam annotation encoded differently.

### Provenance and reproducibility

`extract_cairo.py` prints a clear audit trail (number of collapses, etc.).
Every patch dataset (`word_content_fixes.json`, `word_boundary_fixes.json`,
`sajda_positions.json`) is self-validating: stale entries fail loudly at
extraction time. To regenerate from scratch:

```bash
uv run scripts/extract_cairo.py    # applies normalisations + patches
uv run scripts/convert_to_csv.py   # rebuilds taisir_variants.csv from the JSON
```

The full compare pipeline lives in the parent repository at
`scripts/cairo_review/` and finishes with **0 unresolved differences**
plus a small set of asserted accepted-differences. See that folder's
README for the end-to-end workflow.

## Data Sources

The variants are extracted from multiple historical works documented in Corpus Coranicum:

### Primary Source
- **ad-Dānī (d. 1053 CE): at-Taisīr fī l-qirāʾāt as-sabʿ**
  - The authoritative source for the seven canonical readings
  - All verses have variants from this work

### Additional Sources
- **al-Bannāʾ: Itḥāf fuḍalāʾ al-bašar**
- **Abū Ḥayyān: al-Baḥr al-muḥīṭ**
- Various other classical works

## Transliteration Details

### Corpus Coranicum System

The transliteration follows the Corpus Coranicum standard, which is based on the Deutsche Morgenländische Gesellschaft (DMG) system with some modifications.

#### Special Characters

| Character | Unicode | Name | Example |
|-----------|---------|------|---------|
| ʾ | U+02BE | Hamza | ʾalif |
| ʿ | U+02BF | ʿAyn | ʿabd |
| ā | U+0101 | Long a | qāla |
| ī | U+012B | Long i | fī |
| ū | U+016B | Long u | nūr |
| ḏ | U+1E0F | Ḏāl | ḏālika |
| ḥ | U+1E25 | Ḥāʾ | ḥaqq |
| ḫ | U+1E2B | Ḫāʾ | ḫalq |
| ṣ | U+1E63 | Ṣād | ṣalāt |
| ḍ | U+1E0D | Ḍād | ḍaraba |
| ṭ | U+1E6D | Ṭāʾ | ṭayyib |
| ẓ | U+1E93 | Ẓāʾ | ẓalama |
| ġ | U+0121 | Ġayn | ġafara |
| š | U+0161 | Šīn | šayʾ |
| ǧ | U+01E7 | Ǧīm | ǧanna |
| ṯ | U+1E6F | Ṯāʾ | ṯalāṯa |

#### Imāla (Vowel Fronting)

Some reciters (especially Warš and Qālūn) use imāla:

| Standard | Imāla | Example |
|----------|-------|---------|
| ā | æ | t-tauræti (Warš) vs t-taurāti (Ḥafṣ) |
| ā | ē | t-taurēti (Ibn ʿĀmir) vs t-taurāti (Ḥafṣ) |

#### Assimilation

The transliteration shows assimilation in context:
- `aš-šams` (not `al-šams`)
- `ar-raḥmān` (not `al-raḥmān`)

## Data Quality

### Validation

The dataset passes comprehensive validation tests (see `test_variants.py`):

✅ **Structure Tests**
- All 6,236 verses present (114 surahs)
- No duplicate verses
- Correct verse ordering
- All 7 reciters present in every verse

✅ **Content Tests**
- No empty word values
- Valid word positions (positive integers)
- Complete readings have consecutive word positions
- All variants have source attribution

✅ **Reference Text Tests**
- CSV reference matches Cairo 1924 Quran transliteration
- Total word count: 531,832 entries

### ⚠️ Data Quality Disclaimer

**Important Limitations**: This dataset is scraped from Corpus Coranicum and has the following limitations:

1. **Accuracy Not Guaranteed**: While quality checks are implemented, errors may exist from the source or scraping process.

2. **Incomplete Coverage**: The following variant types are **NOT included** in the Corpus Coranicum at-Taisīr data:
   - **Madd variations** (differences in vowel lengthening)
   - **Hamza tashīl/musahhal** (hamza softening/facilitation)
   - Phonetic variations not represented in transliteration
   - Some subtle pronunciation differences

3. **Source Dependency**: The quality and completeness depend entirely on Corpus Coranicum's data.

**For Scholarly Use**: Always verify critical readings against authoritative printed editions of ad-Dānī's at-Taisīr or other primary sources. This dataset is intended for:
- Computational linguistics and digital humanities research
- Educational and exploratory purposes
- Cross-referencing with primary sources
- Large-scale pattern analysis

### Known Issues and Fixes

The `fix_variants.py` script addresses these issues in the raw data:

1. **Transmitter Linking**
   - Problem: Transmitters appear without reciter context
   - Fix: Links transmitters to their reciters (e.g., "ad-Dūrī" → "3 Abū ʿAmr (ad-Dūrī)")

2. **Duplicate Reciters**
   - Problem: Some verses have duplicate reciter entries
   - Fix: Removes duplicates while preserving unique readings

3. **Special Case: Verse 75:1**
   - Problem: Only al-Bazzī differs (reads both "la-" and "lā"), not Ibn Kaṯīr
   - Fix: Corrects the attribution

### Missing Data

Two verses (10:87 and 19:72) initially had incomplete reference text because:
- No "empty reader" row (base reading)
- Ḥafṣ only had variant words, not complete reading

**Solution**: The `convert_to_csv.py` script uses the reader with the most consecutive words as reference for these special cases.

## Usage Examples

### Python: Load JSON

```python
import json

with open('all_variants_fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Get variants for a specific verse
verse = next(v for v in data if v['surah'] == 2 and v['verse'] == 255)
taisir = [v for v in verse['variants'] if 'at-Taisīr' in v['work']]

print(f"Found {len(taisir)} readings from at-Taisīr")
```

### Python: Load CSV with Pandas

```python
import pandas as pd

df = pd.read_csv('taisir_variants.csv')

# Filter for verses with Warš variants
warsh_variants = df[df['1 Nāfiʿ (Warš)'].notna()]
print(f"Warš differs in {len(warsh_variants)} words")

# Get all variants for Surah Al-Fatiha
fatiha = df[df['surah'] == 1]
```

### JavaScript: Load JSON

```javascript
const fs = require('fs');

const data = JSON.parse(fs.readFileSync('all_variants_fixed.json', 'utf8'));

// Find all verses where Warš differs
const warshVariants = data.filter(verse => 
  verse.variants.some(v => 
    v.reader === '1 Nāfiʿ (Warš)' && 
    Object.keys(v.words).length > 0
  )
);

console.log(`Warš has variants in ${warshVariants.length} verses`);
```

## Statistics

### By Reciter

Approximate number of words where each reciter differs from Ḥafṣ:

| Reciter | Variants | Notes |
|---------|----------|-------|
| Nāfiʿ | ~15,000 | Significant differences, especially Warš |
| Ibn Kaṯīr | ~8,000 | Moderate differences |
| Abū ʿAmr | ~10,000 | Moderate differences |
| Ibn ʿĀmir | ~12,000 | Moderate to significant differences |
| ʿĀṣim (Šuʿba) | ~5,000 | Fewer differences (same reciter as Ḥafṣ) |
| Ḥamza | ~14,000 | Significant differences |
| al-Kisāʾī | ~13,000 | Significant differences |

### Common Variant Types

1. **Orthographic** (ṣirāṭ vs sirāṭ)
2. **Vowel length** (buyūt vs biyūt)
3. **Hamza** (huzuwan vs huzuʾan)
4. **Imāla** (t-taurāta vs t-tauræta)
5. **Pronoun suffixes** (ʿalaihim vs ʿalaihimū)

## Updates and Maintenance

This dataset is based on Corpus Coranicum as of April 2024. To update:

1. Run `node scripts/scrape.js` (takes ~2 hours)
2. Run `uv run scripts/fix_variants.py`
3. Run `uv run scripts/convert_to_csv.py`
4. Run `pytest tests/test_variants.py -v` to validate

## Contact

For questions about the data structure or usage, please open an issue on GitHub.
