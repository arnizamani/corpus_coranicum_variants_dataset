# Data Documentation

## Dataset Overview

This dataset contains word-by-word Quranic variant readings for the seven canonical reciters according to ad-Dānī's *at-Taisīr fī l-qirāʾāt as-sabʿ*.

## Files

### Core Data Files

| File | Size | Format | Description |
|------|------|--------|-------------|
| `all_variants_fixed.json` | ~25 MB | JSON | Complete dataset with all sources and quality fixes applied |
| `taisir_variants.csv` | ~4.5 MB | CSV | Tabular format with **only ad-Dānī's at-Taisīr variants** |
| `cairo_quran.json` | ~10 MB | JSON | Cairo 1924 Quran reference text (Ḥafṣ reading) with transliteration and Arabic |
| `ayah_numbering_variants.csv` | ~11 KB | CSV | Verse ending variants across six classical counting systems |

**Note**: `all_variants.json` (raw scraped data) is not published as it's an intermediate file. Use `all_variants_fixed.json` instead.

**Self-Contained**: All data files are included in this repository. No external dependencies on Corpus Coranicum TEI XML files are needed.

### Code Files

| File | Language | Purpose |
|------|----------|---------|
| `scrape.js` | JavaScript | Main scraper (uses Playwright) |
| `fix_variants.py` | Python | Data quality fixes |
| `convert_to_csv.py` | Python | JSON to CSV converter |
| `extract_cairo.py` | Python | Extract Cairo Quran from TEI XML |
| `test_variants.py` | Python | Validation tests (pytest) |
| `find_multiple_variants.py` | Python | Analysis tool for data quality |

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

1. Run `node scrape.js` (takes ~2 hours)
2. Run `python3 fix_variants.py`
3. Run `python3 convert_to_csv.py`
4. Run `pytest test_variants.py -v` to validate

## Contact

For questions about the data structure or usage, please open an issue on GitHub.
