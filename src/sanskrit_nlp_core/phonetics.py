# coding: utf-8
"""
Comprehensive transliteration and canonicalization utilities for Phase 1.

Provides:
 - IAST <-> Devanagari mappings for canonical Sanskrit phonemes.
 - ascii_to_iast: convert common ASCII approximations to IAST.
 - canonicalize_symbol: normalize input token (ASCII/IAST/Devanagari) -> canonical IAST form.
"""
from typing import Dict
import unicodedata
import re

# Canonical IAST tokens and Devanagari glyphs for standard Sanskrit phonemes
_IAST_TO_DEVANAGARI: Dict[str, str] = {
    # Vowels
    "a": "अ", "ā": "आ", "i": "इ", "ī": "ई", "u": "उ", "ū": "ऊ",
    "ṛ": "ऋ", "ṝ": "ॠ", "ḷ": "ऌ", "ḹ": "ॡ",
    "e": "ए", "ai": "ऐ", "o": "ओ", "au": "औ",
    # Consonants (varṇas)
    "ka": "क", "kha": "ख", "ga": "ग", "gha": "घ", "ṅa": "ङ",
    "ca": "च", "cha": "छ", "ja": "ज", "jha": "झ", "ña": "ञ",
    "ṭa": "ट", "ṭha": "ठ", "ḍa": "ड", "ḍha": "ढ", "ṇa": "ण",
    "ta": "त", "tha": "थ", "da": "द", "dha": "ध", "na": "न",
    "pa": "प", "pha": "फ", "ba": "ब", "bha": "भ", "ma": "म",
    "ya": "य", "ra": "र", "la": "ल", "va": "व",
    "śa": "श", "ṣa": "ष", "sa": "स", "ha": "ह",
    # Special signs
    "ṃ": "ँ",  # anusvāra (candrabindu)
    "ṁ": "ं",  # anusvāra (bindu)
    "ḥ": "ः",  # visarga
    # short markers / single consonants used in sutra notation (approx)
    "k": "क", "g": "ग", "c": "च", "j": "ज", "ṭ": "ट", "ḍ": "ड", "t": "त", "d": "द",
    "p": "प", "b": "ब", "m": "म", "n": "न", "ṅ": "ङ", "ṇ": "ण", "ñ": "ञ",
    "y": "य", "r": "र", "l": "ल", "v": "व", "ś": "श", "ṣ": "ष", "s": "स", "h": "ह",
}

# Build reverse mapping
_DEVANAGARI_TO_IAST: Dict[str, str] = {v: k for k, v in _IAST_TO_DEVANAGARI.items()}

# ASCII approximations commonly used by users / legacy systems -> IAST
# We conservatively map typical forms: aa->ā, ii->ī, uu->ū, r`/rr->ṛ, l`/ll->ḷ, etc.
_ASCII_TO_IAST: Dict[str, str] = {
    "aa": "ā", "ii": "ī", "uu": "ū",
    "ri": "ṛ", "rri": "ṝ", "li": "ḷ", "lli": "ḹ",
    "ai": "ai", "au": "au",
    "sh": "ś", "Sh": "ṣ", "zh": "ṣ",  # common ascii for retroflex s
    "ch": "ch", "jh": "jh", "th": "th", "dh": "dh", "ph": "ph", "bh": "bh",
    "ng": "ṅ", "ṅ": "ṅ", "nj": "ñ", "ny": "ñ",
    "aa": "ā",
    "ṃ": "ṃ", "M": "ṃ", "H": "ḥ",
    # simple single-letter tokens mapping to IAST single letters
    "a": "a", "i": "i", "u": "u", "e": "e", "o": "o",
    "k": "k", "g": "g", "c": "c", "j": "j", "ṭ": "ṭ", "ḍ": "ḍ", "t": "t", "d": "d",
    "p": "p", "b": "b", "m": "m", "n": "n", "y": "y", "r": "r", "l": "l", "v": "v", "s": "s", "h": "h",
}

# Patterns for ascii to IAST tokenization (ordered for longest-first matching)
_ASCII_TOKEN_PATTERNS = [
    ("ai", "ai"), ("au", "au"),
    ("aa", "ā"), ("ii", "ī"), ("uu", "ū"),
    ("rr", "ṛ"), ("ri", "ṛ"), ("rri", "ṝ"),
    ("ll", "ḷ"), ("li", "ḷ"),
    ("sh", "ś"), ("Sh", "ṣ"), ("zh", "ṣ"),
    ("kh", "kh"), ("gh", "gh"), ("ch", "ch"), ("jh", "jh"),
    ("ṭh", "ṭh"), ("ḍh", "ḍh"), ("th", "th"), ("dh", "dh"),
    ("ph", "ph"), ("bh", "bh"),
    ("ng", "ṅ"), ("ṇ", "ṇ"), ("nj", "ñ"), ("ny", "ñ"),
    ("ṃ", "ṃ"), ("M", "ṃ"), ("H", "ḥ"),
    # single letters fallback
    ("a", "a"), ("i", "i"), ("u", "u"), ("e", "e"), ("o", "o"),
    ("k", "k"), ("g", "g"), ("c", "c"), ("j", "j"), ("ṭ", "ṭ"), ("ḍ", "ḍ"),
    ("t", "t"), ("d", "d"), ("p", "p"), ("b", "b"), ("m", "m"), ("n", "n"),
    ("y", "y"), ("r", "r"), ("l", "l"), ("v", "v"), ("s", "s"), ("h", "h"),
]

def normalize_symbol(sym: str) -> str:
    """
    NFC-normalize and trim whitespace.
    """
    if not isinstance(sym, str):
        raise TypeError("symbol must be a string")
    return unicodedata.normalize("NFC", sym.strip())

def iast_to_devanagari(sym: str) -> str:
    """
    Convert a canonical IAST token to Devanagari glyph if mapping exists;
    otherwise return input unchanged.
    """
    s = normalize_symbol(sym)
    return _IAST_TO_DEVANAGARI.get(s, s)

def devanagari_to_iast(sym: str) -> str:
    """
    Convert a single Devanagari glyph to IAST token if mapping exists;
    otherwise return input unchanged.
    """
    s = normalize_symbol(sym)
    return _DEVANAGARI_TO_IAST.get(s, s)

def ascii_to_iast(token: str) -> str:
    """
    Convert a single ASCII token (or short ASCII sequence) into IAST using
    greedy longest-match tokenization. Returns a concatenated IAST string.
    Example: 'aa' -> 'ā', 'ksha' -> 'ksha' (no perfect mapping for conjuncts here).
    """
    s = normalize_symbol(token)
    i = 0
    out = []
    while i < len(s):
        matched = False
        # try longest patterns first
        for pat, iast in _ASCII_TOKEN_PATTERNS:
            if s[i:i+len(pat)] == pat:
                out.append(iast)
                i += len(pat)
                matched = True
                break
        if not matched:
            # Unknown char: emit as-is and advance
            out.append(s[i])
            i += 1
    return "".join(out)

def canonicalize_symbol(token: str) -> str:
    """
    Canonicalize token to a best-effort IAST representation.
    Accepts Devanagari, IAST, or ASCII approximation.
    Steps:
      - If token is entirely Devanagari glyphs mapped, convert each glyph to IAST.
      - Else, try to detect presence of diacritics (IAST) and normalize NFC.
      - Else, apply ascii_to_iast tokenization.
    """
    s = normalize_symbol(token)
    # Quick heuristic: if the token contains Devanagari block chars, convert per glyph
    if any("\u0900" <= ch <= "\u097F" for ch in s):
        # convert each glyph separately where mapping exists
        out = []
        for ch in s:
            iast = devanagari_to_iast(ch)
            out.append(iast if iast else ch)
        return "".join(out)
    # If token contains known diacritic characters (macrons, dots), assume it's IAST already
    if re.search(r"[āīūṛṝḷḹṅñṭḍṇśṣḥṃṁ]", s):
        return s
    # Fallback: ascii approximations
    return ascii_to_iast(s)
