"""Golden tests for transliterate_to_arabic.to_arabic.

Cases live in transliterate_to_arabic_cases.csv (edit that to add/change cases).
"""
import csv
from pathlib import Path

import pytest

from transliterate_to_arabic import to_arabic
from normalize_arabic import normalize

CASES_PATH = Path(__file__).parent / "transliterate_to_arabic_cases.csv"
with open(CASES_PATH, encoding="utf-8") as f:
    CASES = [
        (r["translit"], r["arabic"], r.get("prev_open_tanween") == "1")
        for r in csv.DictReader(f)
    ]


@pytest.mark.parametrize("translit,arabic,prev_open_tanween", CASES)
def test_to_arabic(translit, arabic, prev_open_tanween):
    assert to_arabic(translit, reference=arabic, prev_open_tanween=prev_open_tanween) == normalize(arabic)
