# Corpus Coranicum Quranic Variants Dataset

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Data: CC BY-SA 4.0](https://img.shields.io/badge/Data-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)

A comprehensive dataset of Quranic variant readings (qirāʾāt) for the seven canonical reciters according to ad-Dānī's *at-Taisīr*, scraped from [Corpus Coranicum](https://corpuscoranicum.de) with proper source attribution.

## 📖 Overview

This repository provides:
- **Complete variant readings** for all 6,236 verses of the Quran
- **Seven canonical reciters** (al-qurrāʾ as-sabʿa) with their transmitters
- **Word-by-word variants** in scholarly transliteration
- **Source attribution** from historical works
- **Reference text** from the Cairo 1924 Quran (Hafs reading)
- **Machine-readable formats**: JSON and CSV

### Why This Dataset?

The Corpus Coranicum project provides an invaluable TEI XML export of Quranic variants, but the source attribution fields are empty in their GitHub repository. This scraper extracts the complete data directly from their website, preserving the critical source information that scholars need.

### Why ad-Dānī's at-Taisīr?

The CSV dataset focuses exclusively on **ad-Dānī's *at-Taisīr fī l-qirāʾāt as-sabʿ*** for two important reasons:

1. **Authenticity**: It is the most authoritative and widely-accepted source for the seven canonical readings, compiled by the renowned scholar Abū ʿAmr ad-Dānī (d. 1053 CE).

2. **Completeness**: It is the only source in Corpus Coranicum that provides **complete coverage** of all 6,236 verses of the Quran. Other sources (al-Bannāʾ, Abū Ḥayyān, etc.) offer only partial coverage of specific verses or chapters.

The full JSON dataset (`all_variants_fixed.json`) includes all sources from Corpus Coranicum for researchers who need the additional variant readings.

## 🎯 The Seven Canonical Reciters

According to ad-Dānī's *at-Taisīr fī l-qirāʾāt as-sabʿ* (11th century CE), the seven canonical reciters and their transmitters are:

| # | Reciter (Qāriʾ) | Transmitter 1 (Rāwī) | Transmitter 2 (Rāwī) |
|---|-----------------|---------------------|---------------------|
| 1 | **Nāfiʿ** (d. 169/785) | Qālūn | Warš |
| 2 | **Ibn Kaṯīr** (d. 120/738) | al-Bazzī | Qunbul |
| 3 | **Abū ʿAmr** (d. 154/770) | ad-Dūrī | as-Sūsī |
| 4 | **Ibn ʿĀmir** (d. 118/736) | Hišām | Ibn Ḏakwān |
| 5 | **ʿĀṣim** (d. 127/745) | Šuʿba | **Ḥafṣ** ⭐ |
| 6 | **Ḥamza** (d. 156/772) | Ḫallād | Ḫalaf |
| 7 | **al-Kisāʾī** (d. 189/804) | ad-Dūrī | al-Laiṯ |

⭐ **Ḥafṣ ʿan ʿĀṣim** is the most widely used reading today, forming the basis of most modern Quran publications.

## 📊 Dataset Statistics

- **Total verses**: 6,236 (114 surahs)
- **Total variants**: 531,832 word entries
- **Data sources**: Multiple historical works including:
  - ad-Dānī: *at-Taisīr fī l-qirāʾāt as-sabʿ* (primary source)
  - al-Bannāʾ: *Itḥāf fuḍalāʾ al-bašar*
  - Abū Ḥayyān: *al-Baḥr al-muḥīṭ*
  - And others
- **Reference text**: Cairo 1924 Quran (Ḥafṣ reading) included as `cairo_quran.json`

## 🔤 Transliteration Scheme

The dataset uses the **Corpus Coranicum transliteration system**, a scholarly standard for Arabic:

### Consonants
| Arabic | Trans. | Arabic | Trans. | Arabic | Trans. |
|--------|--------|--------|--------|--------|--------|
| ء | ʾ | ذ | ḏ | ض | ḍ |
| ب | b | ر | r | ط | ṭ |
| ت | t | ز | z | ظ | ẓ |
| ث | ṯ | س | s | ع | ʿ |
| ج | ǧ | ش | š | غ | ġ |
| ح | ḥ | ص | ṣ | ف | f |
| خ | ḫ | ض | ḍ | ق | q |

### Vowels
- **Short vowels**: a, i, u
- **Long vowels**: ā, ī, ū
- **Diphthongs**: ai, au
- **Imāla** (vowel fronting): æ, ē (used by some reciters like Warš)

### Special Notations
- **Hamza variants**: ʾ (hamza)
- **Assimilation**: Indicated in context (e.g., *aš-šams*)
- **Pausal forms**: May differ from contextual forms

## 📁 Data Format

### JSON Structure (`all_variants_fixed.json`)

**Note**: Only `all_variants_fixed.json` is published. The raw `all_variants.json` is an intermediate file generated during scraping and is not needed.

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

**Fields:**
- `surah`: Surah number (1-114)
- `verse`: Verse number (1-indexed)
- `work`: Source book with author and date
- `reader`: Reciter or transmitter name
- `words`: Object with word positions (1-indexed) as keys
  - For complete readings: all word positions present
  - For variants: only differing words present

### CSV Structure (`taisir_variants.csv`)

**Note**: This CSV contains only variants from **ad-Dānī's at-Taisīr** (the seven canonical readings). Other sources in the JSON are not included.

| Column | Description |
|--------|-------------|
| `surah` | Surah number |
| `verse` | Verse number |
| `word` | Word position (1-indexed) |
| `reference` | Reference text (transliteration) |
| `reference_cairo` | Cairo 1924 Arabic text |
| `1 Nāfiʿ` ... `7 al-Kisāʾī` | Reciter variants (when both transmitters agree) |
| `1 Nāfiʿ (Qālūn)` ... | Individual transmitter variants |

**CSV Logic:**
- **Reciter columns**: Filled when both transmitters agree and differ from reference
- **Transmitter columns**: Filled when transmitters disagree
- **Empty cells**: Reading matches the reference (Ḥafṣ)

### Cairo Quran Reference (`cairo_quran.json`)

The Cairo 1924 Quran text (Ḥafṣ reading) is provided as a standalone reference:

```json
{
  "source": "Cairo 1924 Quran (Corpus Coranicum TEI XML)",
  "edition": "King Fuʾād edition, Amīrī Press, Būlāq (Cairo), 1924",
  "reading": "Ḥafṣ ʿan ʿĀṣim",
  "orthography": "rasm ʿuṯmānī (Uthmanic script)",
  "total_verses": 6236,
  "verses": [
    {
      "surah": 1,
      "verse": 1,
      "words": [
        {
          "position": 1,
          "transliteration": "bi-smi",
          "arabic": "بِسۡمِ"
        },
        {
          "position": 2,
          "transliteration": "llāhi",
          "arabic": "ٱللَّهِ"
        }
      ]
    }
  ]
}
```

This file is extracted from the Corpus Coranicum TEI XML and provides both transliteration and Arabic text for all 6,236 verses. **This makes the repository self-contained** - no external files are needed for data processing or validation.

## 🚀 Quick Start

### Prerequisites

This repository is **self-contained** and does not require access to external Corpus Coranicum files.

**For scraping (optional):**
```bash
# Node.js dependencies
npm install

# Install Chromium browser
npx playwright install chromium
```

**For data processing:**
```bash
# Python dependencies (handled by uv)
# No additional setup needed
```

### Using the Pre-scraped Data

The repository includes pre-scraped data, so you can start using it immediately:

```python
import json

# Load the fixed variants
with open('all_variants_fixed.json', 'r', encoding='utf-8') as f:
    variants = json.load(f)

# Example: Get all variants for verse 1:1
verse_1_1 = next(v for v in variants if v['surah'] == 1 and v['verse'] == 1)
print(f"Found {len(verse_1_1['variants'])} variant readings")
```

Or use the CSV:

```python
import pandas as pd

df = pd.read_csv('taisir_variants.csv')
# Filter for a specific verse
verse_data = df[(df['surah'] == 1) & (df['verse'] == 1)]
```

### Scraping Fresh Data (Optional)

⚠️ **Warning**: Scraping takes ~2 hours and makes 6,236 HTTP requests. Only run if you need updated data.

```bash
# Scrape all verses
node scrape.js

# The script automatically:
# 1. Scrapes all 6,236 verses
# 2. Saves progress every 50 verses
# 3. Runs fix_variants.py to clean the data
# 4. Generates all_variants_fixed.json
```

### Data Processing

```bash
# Fix data quality issues (already done if you scraped)
python3 fix_variants.py

# Convert to CSV format
python3 convert_to_csv.py

# Run validation tests
uv run pytest test_variants.py -v
```

## 🔍 Data Quality

The dataset includes comprehensive validation tests:

```bash
uv run pytest test_variants.py -v
```

**Tests verify:**
- ✅ All 6,236 verses present
- ✅ All 7 canonical reciters in every verse
- ✅ No duplicate entries
- ✅ Correct verse ordering
- ✅ No empty word values
- ✅ Valid word positions
- ✅ Source attribution present
- ✅ Complete readings have no gaps
- ✅ Reference text matches Cairo 1924 Quran

### Known Data Quality Issues

The `fix_variants.py` script addresses several issues in the raw scraped data:

1. **Transmitter linking**: Links transmitters to their reciters (e.g., "ad-Dūrī" → "3 Abū ʿAmr (ad-Dūrī)")
2. **Duplicate removal**: Removes duplicate reciter entries
3. **Special cases**: Handles verse 75:1 where only al-Bazzī differs

## 📚 Reference Text

The **reference text** in this dataset is the **Cairo 1924 Quran** (Ḥafṣ ʿan ʿĀṣim reading), not the Madinah Mushaf. This is the standard used by Corpus Coranicum.

**Key differences from Madinah Mushaf:**
- Orthography follows the *rasm ʿuṯmānī* (Uthmanic script)
- Some spelling variations in hamza and long vowels
- Verse numbering follows Hafs system (6,236 total verses)

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Additional data validation tests
- Conversion to other formats (SQL, Parquet, etc.)
- Analysis tools and visualizations
- Documentation improvements
- Bug fixes in data processing

## 📄 License

- **Code**: MIT License
- **Data**: CC BY-SA 4.0 (following Corpus Coranicum's license)

## 🙏 Acknowledgments

- **Corpus Coranicum** project for providing the original data
- **Berlin-Brandenburg Academy of Sciences and Humanities** for hosting Corpus Coranicum
- All the scholars who compiled and verified these variant readings over centuries

## 📖 Citation

If you use this dataset in your research, please cite:

```bibtex
@dataset{corpus_coranicum_variants_2026,
  title={Corpus Coranicum Quranic Variants Dataset},
  author={Abdul Rahim Nizamani},
  year={2026},
  publisher={GitHub},
  url={https://github.com/arnizamani/corpus_coranicum_variants_scrapper}
}
```

And cite the original Corpus Coranicum project:

```bibtex
@misc{corpus_coranicum,
  title={Corpus Coranicum},
  author={{Berlin-Brandenburg Academy of Sciences and Humanities}},
  url={https://corpuscoranicum.de},
  note={Accessed: 2026}
}
```

## 📞 Contact

For questions, issues, or suggestions, please open an issue on GitHub.

---

**Note**: This is an independent project and is not officially affiliated with Corpus Coranicum or the Berlin-Brandenburg Academy of Sciences and Humanities.
