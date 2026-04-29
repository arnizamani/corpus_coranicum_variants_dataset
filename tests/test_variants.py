import json
import unittest
import csv
from pathlib import Path

with open(Path(__file__).parent.parent / "data" / "all_variants_fixed.json") as f:
    data = json.load(f)

# Ayah counts per surah (Hafs numbering), from scrape.js
AYAH_COUNTS = [
    7, 286, 200, 176, 120, 165, 206, 75, 129, 109,
    123, 111, 43, 52, 99, 128, 111, 110, 98, 135,
    112, 78, 118, 64, 77, 227, 93, 88, 69, 60,
    34, 30, 73, 54, 45, 83, 182, 88, 75, 85,
    54, 53, 89, 59, 37, 35, 38, 29, 18, 45,
    60, 49, 62, 55, 78, 96, 29, 22, 24, 13,
    14, 11, 11, 18, 12, 12, 30, 52, 52, 44,
    28, 28, 20, 56, 40, 31, 50, 40, 46, 42,
    29, 19, 36, 25, 22, 17, 19, 26, 30, 20,
    15, 21, 11, 8, 8, 19, 5, 8, 8, 11,
    11, 8, 3, 9, 5, 4, 7, 3, 6, 3,
    5, 4, 5, 6,
]


SEVEN_READERS = {
    "1 Nāfiʿ", "2 Ibn Kaṯīr", "3 Abū ʿAmr",
    "4 Ibn ʿĀmir", "5 ʿĀṣim", "6 Ḥamza", "7 al-Kisāʾī",
}


class TestVariantsStructure(unittest.TestCase):
    def test_surah_count(self):
        surahs = {entry["surah"] for entry in data}
        self.assertEqual(len(surahs), 114)

    def test_ayah_count(self):
        self.assertEqual(len(data), 6236)

    def test_no_failed_entries(self):
        failed = [e for e in data if not e.get("success")]
        self.assertEqual(failed, [], f"{len(failed)} failed entries in data")

    def test_no_duplicate_ayahs(self):
        from collections import Counter
        pairs = [(e["surah"], e["verse"]) for e in data]
        dups = [p for p, c in Counter(pairs).items() if c > 1]
        self.assertEqual(dups, [], f"Duplicate (surah, verse) pairs: {dups}")

    def test_entries_sorted_by_surah_verse(self):
        pairs = [(e["surah"], e["verse"]) for e in data]
        self.assertEqual(pairs, sorted(pairs))

    def test_ad_dani_at_least_seven_recitations(self):
        lacking = [
            (e["surah"], e["verse"])
            for e in data
            if sum(1 for v in e["variants"] if "ad-Dānī" in (v["work"] or "")) < 7
        ]
        self.assertEqual(lacking, [], f"{len(lacking)} ayahs have fewer than 7 ad-Dānī rows")

    def test_all_seven_numbered_readers_in_taisir(self):
        missing = [
            (e["surah"], e["verse"])
            for e in data
            if not SEVEN_READERS <= {v["reader"] for v in e["variants"] if "at-Taisīr" in (v["work"] or "")}
        ]
        self.assertEqual(missing, [], f"{len(missing)} ayahs missing a numbered reader in at-Taisīr")

    def test_total_word_count(self):
        total = sum(len(v["words"]) for e in data for v in e["variants"])
        # 531830 reflects the current corpus after manual corrections; the
        # original scrape had 531828. Update this constant when adding or
        # removing words via fix_variants.py or data corrections.
        self.assertEqual(total, 531830)

    def test_no_empty_word_values(self):
        empty = [
            (e["surah"], e["verse"], v["reader"], k)
            for e in data for v in e["variants"]
            for k, w in v["words"].items() if not w.strip()
        ]
        self.assertEqual(empty, [], f"{len(empty)} empty word values")

    def test_word_positions_are_positive_integers(self):
        bad = [
            (e["surah"], e["verse"], k)
            for e in data for v in e["variants"]
            for k in v["words"] if not k.isdigit() or int(k) < 1
        ]
        self.assertEqual(bad, [], f"{len(bad)} invalid word position keys")

    def test_all_variants_have_work(self):
        missing = [
            (e["surah"], e["verse"])
            for e in data for v in e["variants"]
            if not (v.get("work") or "").strip()
        ]
        self.assertEqual(missing, [], f"{len(missing)} variants with missing work")

    def test_known_sources_present(self):
        all_works = {v["work"] for e in data for v in e["variants"]}
        for expected in ["al-Bannāʾ", "Abū Ḥayyān", "ad-Dānī"]:
            self.assertTrue(
                any(expected in (w or "") for w in all_works),
                f"Expected source not found: {expected}",
            )

    def test_hafs_has_complete_reading(self):
        """The at-Taisir row with the most words must have consecutive word positions (no gaps)."""
        incomplete = []
        for e in data:
            taisir = [v for v in e["variants"] if "at-Taisīr" in (v["work"] or "")]
            if not taisir:
                continue
            full_row = max(taisir, key=lambda v: len(v["words"]))
            positions = sorted(int(k) for k in full_row["words"])
            if positions != list(range(positions[0], positions[-1] + 1)):
                incomplete.append((e["surah"], e["verse"]))
        self.assertEqual(incomplete, [], f"{len(incomplete)} ayahs with gaps in at-Taisīr row")

    def test_csv_reference_matches_cairo_xml(self):
        """CSV reference text (column 4) should match Cairo Quran XML transliteration."""
        csv_path = Path(__file__).parent.parent / "data" / "taisir_variants.csv"
        cairo_path = Path(__file__).parent.parent / "data" / "cairo_quran.json"
        
        if not cairo_path.exists():
            self.skipTest(f"Cairo Quran data not found at {cairo_path}")
        
        # Load Cairo Quran data
        with open(cairo_path, 'r', encoding='utf-8') as f:
            cairo_data = json.load(f)
        
        # Build lookup dictionary
        cairo_text = {}
        for verse in cairo_data['verses']:
            surah = verse['surah']
            verse_num = verse['verse']
            words = {str(w['position']): w['transliteration'] for w in verse['words']}
            cairo_text[(surah, verse_num)] = words
        
        # Read CSV
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            mismatches = []
            
            for row in reader:
                surah = int(row['surah'])
                verse = int(row['verse'])
                word_pos = row['word']
                csv_word = row['reference']
                
                cairo_word = cairo_text.get((surah, verse), {}).get(word_pos)
                
                if cairo_word is None:
                    mismatches.append((surah, verse, word_pos, 'missing in Cairo data', csv_word))
                elif cairo_word != csv_word:
                    mismatches.append((surah, verse, word_pos, cairo_word, csv_word))
        
        self.assertEqual(mismatches, [], f"{len(mismatches)} mismatches between CSV and Cairo Quran. First 10: {mismatches[:10]}")
