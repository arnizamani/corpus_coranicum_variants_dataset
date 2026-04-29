"""Walk taisir_variants.csv word-by-word converting each transliteration to
Arabic, stopping at the first failure. Writes two outputs:

- tests/transliterate_to_arabic_cases.csv: locked successes (append-only).
- tests/transliterate_debug.csv: full trace of each row walked (translit,
  cairo, normalized, generated, status), up to and including the first failure.
"""
import csv
from pathlib import Path

from transliterate_to_arabic import to_arabic
from normalize_arabic import normalize

ROOT = Path(__file__).resolve().parent.parent.parent
SRC = ROOT / "data" / "taisir_variants.csv"
CASES = ROOT / "tests" / "transliterate_to_arabic_cases.csv"
DEBUG = ROOT / "tests" / "transliterate_debug.csv"


def main():
    seen, passed, debug = set(), [], []
    first_fail = None
    prev_open_tanween = False  # first word of Quran has no predecessor
    with open(SRC, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            t, a = row["reference"], row["reference_cairo"]
            if t in seen:
                # Don't update prev flag for skipped duplicates — we must
                # still track the flag to preserve ayah-order semantics.
                prev_open_tanween = '\u06ED' in a
                continue
            seen.add(t)
            norm = normalize(a)
            try:
                got = to_arabic(t, reference=a, prev_open_tanween=prev_open_tanween)
                status = "ok" if got == norm else "mismatch"
            except Exception as e:
                got, status = "", f"error: {type(e).__name__}: {e}"
            debug.append((t, a, norm, got, status))
            if status == "ok":
                passed.append((t, a, prev_open_tanween))
            else:
                first_fail = debug[-1]
                break
            prev_open_tanween = '\u06ED' in a

    with open(CASES, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["translit", "arabic", "prev_open_tanween", "note"])
        for t, a, pot in passed:
            w.writerow([t, a, "1" if pot else "0", ""])

    with open(DEBUG, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["translit", "cairo", "normalized", "generated", "status"])
        w.writerows(debug)

    print(f"passed: {len(passed)}; first failure: {first_fail}")


if __name__ == "__main__":
    main()
