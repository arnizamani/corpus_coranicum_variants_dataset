"""Convert Corpus Coranicum transliteration to basic vocalized Arabic (Imlāʾī rasm).

v0: simple words only (consonants + short/long vowels + shadda). Raises
NotImplementedError for anything containing features we have not handled yet
(hamza, ʿayn, definite article, prefixes, alternation, imāla, parentheses, …).
"""

from normalize_arabic import normalize

# Single-letter consonants (after multi-char ones are consumed).
CONSONANTS = {
    'b': 'ب', 't': 'ت', 'ǧ': 'ج', 'ḥ': 'ح', 'ḫ': 'خ',
    'd': 'د', 'r': 'ر', 'z': 'ز', 's': 'س', 'š': 'ش',
    'ṣ': 'ص', 'ḍ': 'ض', 'ṭ': 'ط', 'ẓ': 'ظ', 'ġ': 'غ',
    'f': 'ف', 'q': 'ق', 'k': 'ك', 'l': 'ل', 'm': 'م',
    'n': 'ن', 'h': 'ه', 'w': 'و', 'y': 'ي',
    'ṯ': 'ث', 'ḏ': 'ذ',
    'ʿ': 'ع',
}
SHORT_VOWELS = {'a': '\u064E', 'i': '\u0650', 'u': '\u064F'}  # fatha, kasra, damma
LONG_VOWELS = {'ā': ('\u064E', 'ا'), 'ī': ('\u0650', 'ي'), 'ū': ('\u064F', 'و')}
SHADDA = '\u0651'
SUKUN = '\u06E1'  # small high dotless head of khah (Cairo convention)

UNHANDLED = set("|/*()æēäăĭ·…I")

WASLA = '\u0671'  # alef wasla
LAM = '\u0644'
SUN_LETTERS = set("tṯdḏrzsšṣḍṭẓln")

# Allāh stem: `llā` before `h` is written with two explicit lāms (first sukun,
# second shadda+fatha) and no medial alef. We match `llā` when followed by `h`
# and emit its Arabic unit, leaving the `h` for the main loop to handle with
# its trailing vowel.
_ALLAH_TRIGGER = 'llā'
_ALLAH_ARABIC = '\u0644\u0644\u0651\u064E'  # ل ل ّ َ (standard: two lāms)
_ALLAH_ARABIC_AFTER_L = '\u0644\u0651\u064E'  # ل ّ َ (elided after li-: one lām)

# Muqaṭṭaʿāt (disjointed letters at the start of some surahs). Hardcoded
# because their transliteration spells out letter names but the Arabic is the
# literal letter glyphs with maddah (U+0653). Entries added only as they
# trigger in the dataset walk.
_MUQATTAAT = {
    'ʾalif-lām-mīm': 'ال\u0653م\u0653',
}


def _starts_with_two_consonants(s: str) -> bool:
    """True if s starts with two consonants and no vowel (or dash) between them."""
    return len(s) >= 2 and s[0] in CONSONANTS and s[1] in CONSONANTS


def to_arabic(
    translit: str,
    reference: str | None = None,
    prev_open_tanween: bool = False,
) -> str:
    """Convert a transliteration to basic Imlāʾī Arabic.

    If `reference` is provided (normalized Arabic text), trailing letters from
    the reference that the generator did not produce (e.g. pausal alef, ة,
    tanween-alef) are appended to repair the spelling.

    If `prev_open_tanween` is True (previous word ended in open tanween,
    marked in Cairo text with U+06ED small low meem) and the current word
    starts with `l` or `r`, a shadda is placed on that first consonant.
    """
    if translit in _MUQATTAAT:
        return _MUQATTAAT[translit]
    if any(c in UNHANDLED for c in translit):
        raise NotImplementedError(f"unsupported feature in {translit!r}")
    if not translit or (translit[0] not in CONSONANTS and translit[0] != 'ʾ'):
        raise NotImplementedError(f"word must start with a consonant: {translit!r}")

    # Allāh stem: wherever `llāh` appears, the `llā` part is written with two
    # explicit lāms and no alef. We handle this inside the main loop below.
    s = translit

    out = []
    # Definite article: input of the form `X-Y…` where the first segment has
    # no vowel (bare consonant before `-`). Two cases:
    #   - Sun letter (X == Y, X in SUN_LETTERS): wasla + bare lām, then let
    #     the main loop double-process `Y` for shadda.
    #   - Moon letter (X == 'l', Y any consonant): wasla + lām + sukun, then
    #     let the main loop process `Y` normally.
    if len(s) >= 3 and s[1] == '-' and s[0] in CONSONANTS and s[2] in CONSONANTS:
        if s[0] in SUN_LETTERS and s[0] == s[2]:
            out.append(WASLA)
            out.append(LAM)
            # Drop the bare consonant + dash; the main loop will see `Y…` and
            # we prepend an extra `Y` so it emits Y + shadda + vowel.
            s = s[2:]
            s = s[0] + s
        elif s[0] == 'l':
            out.append(WASLA)
            out.append(LAM)
            out.append(SUKUN)
            s = s[2:]

    if not out and _starts_with_two_consonants(s):
        out.append(WASLA)
    i = 0
    n = len(s)

    while i < n:
        # Allāh stem match: `llā` followed by `h`.
        if s.startswith(_ALLAH_TRIGGER, i) and i + 3 < n and s[i + 3] == 'h':
            # Elision: `l<vowel>-llāh` (e.g. `li-llāh`) drops the first lām.
            after_l_prefix = (
                i >= 3 and s[i - 1] == '-'
                and s[i - 2] in SHORT_VOWELS
                and s[i - 3] == 'l'
            )
            out.append(_ALLAH_ARABIC_AFTER_L if after_l_prefix else _ALLAH_ARABIC)
            i += 3  # consume l,l,ā; leave h for normal processing
            continue
        c = s[i]
        if c == '-':
            i += 1
            continue
        # Word-initial hamza (or hamza after a dash-joined prefix).
        if c == 'ʾ' and (i == 0 or s[i - 1] == '-'):
            nxt = s[i + 1] if i + 1 < n else ''
            if nxt == 'ā':
                out.append('\u0622')  # alef madda
                i += 2
            elif nxt == 'i':
                out.append('\u0625')  # alef hamza below
                out.append(SHORT_VOWELS['i'])
                i += 2
            elif nxt in ('a', 'u'):
                out.append('\u0623')  # alef hamza above
                out.append(SHORT_VOWELS[nxt])
                i += 2
            else:
                raise NotImplementedError(f"initial ʾ followed by {nxt!r} in {translit!r}")
            continue
        if c in CONSONANTS:
            out.append(CONSONANTS[c])
            nxt = s[i + 1] if i + 1 < n else ''
            doubled = nxt == c
            if doubled:
                i += 2
                nxt = s[i] if i < n else ''
            else:
                i += 1
            # Emit shadda (if doubled) before the haraka — matches modern
            # Arabic typing convention (shadda + haraka).
            if doubled:
                out.append(SHADDA)
            if nxt in SHORT_VOWELS:
                out.append(SHORT_VOWELS[nxt])
                i += 1
                # Diphthong: 'a' + ('u'|'i') → fatha + wāw/yā with sukun.
                if nxt == 'a' and i < n and s[i] in ('u', 'i'):
                    out.append(CONSONANTS['w'] if s[i] == 'u' else CONSONANTS['y'])
                    out.append(SUKUN)
                    i += 1
            elif nxt in LONG_VOWELS:
                hrk, letter = LONG_VOWELS[nxt]
                out.append(hrk)
                out.append(letter)
                i += 1
            else:
                out.append(SUKUN)
            continue
        raise NotImplementedError(f"unhandled char {c!r} in {translit!r}")

    result = ''.join(out)
    # Idgham: if previous word ended in open tanween and this word starts
    # with `l` or `r`, put a shadda on that first letter.
    if prev_open_tanween and translit[:1] in ('l', 'r'):
        # Insert shadda right after the first consonant letter in `result`
        # (skip any leading wasla-alef).
        pos = 1 if result[:1] == WASLA else 0
        result = result[: pos + 1] + SHADDA + result[pos + 1:]
    if reference is not None:
        ref = normalize(reference)
        # Prefix repair: reference has extra trailing chars (pausal alef, ة…).
        if ref.startswith(result) and len(ref) > len(result):
            result = ref
        else:
            # Tanween repair: generator renders '-an/-in/-un' as vowel+nūn+sukun
            # but the reference may spell it as tanween (± trailing alef or ى).
            # If stripping our vowel+nūn+sukun tail yields a prefix of ref that
            # continues with the matching tanween, adopt the reference's tail.
            for vowel, *tanweens in (
                ('\u064E', '\u064B', '\u08F0'),  # fatha → fathatan or open fathatan
                ('\u0650', '\u064D', '\u08F1'),  # kasra → kasratan or open kasratan
                ('\u064F', '\u064C', '\u08F2'),  # damma → dammatan or open dammatan
            ):
                tail = vowel + '\u0646' + SUKUN  # vowel + ن + sukun
                if result.endswith(tail):
                    stem = result[: -len(tail)]
                    matched = False
                    for tanween in tanweens:
                        if ref.startswith(stem + tanween):
                            result = ref
                            matched = True
                            break
                    if matched:
                        break
    return result
