# TODO

## Transliteration → Arabic for all variants

Provide an Arabic rendering of every transliterated variant reading in
`taisir_variants.csv` (the per-reader transliteration columns).

This includes handling transliteration patterns specific to variants:
imālah, ishmām, ikhtilās, silent/elided letters, open-tanween joins across
word boundaries, pausal vs. continuous forms, etc.

## Make Cairo text Unicode-compliant

`reference_cairo` currently contains a few non-Unicode hacks that only render
correctly in the Cairo Quran font (private-use code points, font-specific
shaping tricks, etc.). Replace them with standard Unicode so the text renders
correctly in any Unicode-conformant font.

Tasks:

- Enumerate every non-Unicode / font-hack code point currently present in
  `reference_cairo` (and `cairo_quran.json`).
- For each, pick the correct standard Unicode replacement, preferring code
  points supported by Scheherazade New font (which is the only font with 100%
  of all Arabic code points in Unicode, excluding the presentation forms).
- Save the Unicode-compliant text in `taisir_variants.csv`.

Both tasks touch Quranic text data files, so follow the "Quranic text
integrity" rule: propose diffs, verify letter-by-letter, never
bulk-rewrite without explicit approval.


## Documentation / metadata

- Verify the 2nd transmitter of al-Kisāʾī labelled "al-Laiṯ" in `README.md`,
  `DATA.md` and the `7 al-Kisāʾī (al-Laiṯ)` column of `taisir_variants.csv`.
  The canonical second transmitter is Abū al-Ḥāriṯ; if Corpus Coranicum
  itself uses al-Laiṯ, document why so readers aren't confused.
- `README.md` lists `ä, ă, ĭ` as ḥarakāt, but the generator treats them as
  unsupported. Either drop them from the README table or mark as
  "not yet handled".
- Single source of truth for the dataset version: `CITATION.cff` says
  `1.0.0`, `pyproject.toml` says `1.0.0`, `README.md`/`PUBLISH.md` say
  "Initial release". Pick one and keep them in sync on every bump.
- `PUBLISH.md` is currently in `.gitignore` — the published repo ships
  without its own publishing guide. Either un-ignore it or explicitly move
  internal docs to a `dev-docs/` folder.
- `extract_cairo.py` expects a TEI XML at
  `../corpus-coranicum-tei/data/cairo_quran/cairoquran.xml` with no
  documentation of where to obtain it. Add a pointer in `DATA.md` or a
  fetch script so the Cairo JSON regeneration path isn't a black box.

## Repo cleanup

- Audit what's actually tracked in git (`node_modules/`, `.venv/`,
  `__pycache__/`, `.pytest_cache/`, `corpus_coranicum_variants.egg-info/`
  should all be excluded in practice, not only in `.gitignore`).
- `diagnose_matching.py` opens `Quran_corpus_10readings/Variant ends of
  ayaat.xlsx` via a relative path that only works from the parent repo's
  root. It depends on a file outside this submodule and shouldn't ship as
  part of the public dataset. Move it to the parent repo, or guard the
  path and skip gracefully.
- `all_variants.json` (25 MB raw scrape) is still tracked even though
  `.gitignore` claims it's excluded and the docs say it shouldn't be
  published. Pick one stance and enforce it.

## Code quality

- `fix_variants.py` scans all 6236 verses once per entry in
  `POSITION_FIXES` / `WORD_OVERRIDES` / `READER_LIST_OVERRIDES`. Index the
  fix tables by `(surah, verse)` once and look up per verse — cleaner and
  faster.
- `convert_to_csv.py` inlines the 7 reciters × 2 transmitters list and
  re-parses reader names with `reciter.split()`. Extract a single
  `RECITERS = [(num, name, [transmitter1, transmitter2]), …]` constant and
  drive both generation and detection from it.
- `_starts_with_two_consonants` in `transliterate_to_arabic.py` doesn't
  treat hamza (`ʾ`) as a consonant, even though hamza is a consonant
  elsewhere in the generator. Decide whether initial `ʾC…` should trigger
  the wasla-alef branch and document the chosen behaviour.
- `scrape.js` launches a fresh Chromium per verse (6236 launches) — huge
  overhead. Reuse one browser/page across verses; expected 5–10× speedup.
- `scrape.js` hardcodes output to `../tmp/scraped_variants/` (writes
  outside the submodule). Make it write inside the submodule (or a
  configurable path) so `node scrape.js` from a fresh clone works
  without a surrounding parent repo.
- `convert_ayah_variants.py` prints rich progress to stdout but has no
  `--quiet` flag and no return value or summary assertion. Add a final
  summary line (counts matched / skipped) and consider a `--quiet` flag
  for CI use.

## Testing

- `tests/test_ayah_variants.py` uses bare `assert` + `print` + an
  `if __name__ == "__main__"` runner. Unify on pytest style (like
  `test_transliterate_to_arabic.py`) and drop the redundant `print` lines.
- `test_variants.py::test_total_word_count` hardcodes `531828`. When a
  future data fix adds or removes a word, the test fails opaquely. Either
  assert a plausible range, or compute the expected total from
  `cairo_quran.json` so the error points at the root cause.
- No direct tests for `normalize_arabic.normalize`. Add a small unit-test
  file covering dagger alef → full alef, open-tanween mapping,
  `haraka + shadda` reorder, mid-word alef-madda → plain alef.
- No CI workflow. Add a minimal GitHub Actions job that runs
  `uv sync && uv run pytest` on push and PR.

## Data / schema

- Add a `reference_madinah` column to `taisir_variants.csv` with the
  Madinah Mushaf Arabic text alongside `reference_cairo` (also tracked in
  the parent repo's TODO).
- `ayah_numbering_variants.csv` never has zero values because loaders
  fall back to Kufi when a cell is empty. Either drop the fallback or
  document in `DATA.md` that empty cells in the source Excel mean
  "agrees with Kufi".
- Publish a `sha256sums.txt` of the three data files (`all_variants_fixed.json`,
  `taisir_variants.csv`, `cairo_quran.json`) so users can verify the copy
  they cloned.

All data-related items touch Quranic text and must follow the
"Quranic text integrity" rule: propose diffs, verify letter-by-letter,
never bulk-rewrite without explicit approval.
