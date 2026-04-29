"""Normalize Cairo Quranic orthography to basic Imlāʾī rasm for comparison.

Rules:
- Dagger (superscript) alef → full alef.
- Strip Quranic recitation/pause marks.
- Reorder haraka + shadda → shadda + haraka (modern typing convention).
- Mid-word alef-madda → plain alef.

Both sides of comparison use U+06E1 (small high dotless head of khah) for sukun.
"""
import re

_SUKUN_MAP = str.maketrans({
    '\u0670': '\u0627',  # dagger (superscript) alef → full alef
})

# Quranic recitation/pause marks to strip (they are not part of the word).
_STRIP = re.compile(r'[\u06D6-\u06DC\u06DF-\u06E0\u06E2-\u06E4\u06E7-\u06E8\u06EA-\u06ED]')

# Any short vowel / tanween / sukun / dagger-alef immediately followed by shadda.
_HARAKA_SHADDA = re.compile(r'([\u064B-\u0650\u06E1\u0670])(\u0651)')


# Open tanween: regular tanween followed by U+06ED (small low meem) → the
# dedicated open-tanween code point. Must run before _STRIP removes U+06ED.
_OPEN_TANWEEN = {
    '\u064B\u06ED': '\u08F0',  # open fathatan
    '\u064D\u06ED': '\u08F1',  # open kasratan
    '\u064C\u06ED': '\u08F2',  # open dammatan
}


def normalize(text: str) -> str:
    text = text.translate(_SUKUN_MAP)
    for k, v in _OPEN_TANWEEN.items():
        text = text.replace(k, v)
    text = _STRIP.sub('', text)
    text = _HARAKA_SHADDA.sub(r'\2\1', text)
    # Mid-word alef-madda (U+0622) → plain alef (U+0627). Preserve at word start.
    if len(text) > 1:
        text = text[0] + text[1:].replace('\u0622', '\u0627')
    return text
