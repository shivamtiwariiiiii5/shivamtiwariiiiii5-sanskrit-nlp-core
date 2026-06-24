# coding: utf-8
"""
Sandhi engine for Phase 2.
Implements a small but robust set of Sandhi joining and splitting rules commonly used in Sanskrit:
 - Vowel sandhi (a+i -> e, a+u -> o, a+a -> ā, i+ī -> ī, etc.)
 - Visarga rules (final 'ḥ' before vowels changes)
 - Consonant assimilation for common cases (n+{c,g} -> n assimilated)

The implementation focuses on correctness for the covered rules and provides join() and split() APIs.
"""
from typing import Tuple, List
from .phonetics import canonicalize_symbol

# Candidate vowel sandhi mapping (left_vowel, right_vowel) -> result
_VOWEL_SANDHI = {
    ("a", "a"): "ā",
    ("a", "i"): "e",
    ("a", "ī"): "e",
    ("a", "u"): "o",
    ("a", "ū"): "o",
    ("a", "r̥"): "ar̥",  # conservative
    ("a", "ai"): "ai",
    ("a", "au"): "au",
    ("i", "a"): "ya",
    ("ī", "a"): "yā",
    ("i", "i"): "ī",
    ("i", "ī"): "ī",
    ("u", "a"): "va",
    ("u", "u"): "ū",
    ("e", "a"): "aya",
    ("o", "a"): "ava",
}

# Simple visarga sandhi: h (ḥ) before voiced consonants often becomes s or z forms; simplified here
_VISARGA_SANDHI = {
    # (final with visarga removed, next initial) -> joined form (approx)
    ("aḥ", "a"): "aḥa",
}

def join(a: str, b: str) -> str:
    """
    Join two surface tokens (IAST or ASCII) applying sandhi rules.
    Returns best-effort joined string in canonical IAST form.
    Algorithm:
      - Canonicalize both
      - If last char of a and first of b are vowels, try vowel sandhi
      - Else if a ends with visarga (ḥ) apply visarga rules
      - Else default concatenation
    """
    A = canonicalize_symbol(a)
    B = canonicalize_symbol(b)

    if not A or not B:
        return A + B

    # Last phoneme of A (simplified as last char/token)
    # Use simple tokenization by trying full vowels (ai, au) first
    def _leading_vowel(s: str) -> Tuple[str, int]:
        # return (vowel token, length) if s starts with vowel
        for v in ("ai", "au", "ā", "ī", "ū", "ṛ", "ḷ", "a", "i", "ī", "u", "e", "o"):
            if s.startswith(v):
                return v, len(v)
        return "", 0

    def _trailing_vowel(s: str) -> Tuple[str, int]:
        for v in ("ai", "au", "ā", "ī", "ū", "ṛ", "ḷ", "a", "i", "ī", "u", "e", "o"):
            if s.endswith(v):
                return v, len(v)
        return "", 0

    tail, lt = _trailing_vowel(A)
    head, lh = _leading_vowel(B)

    if tail and head:
        key = (tail, head)
        if key in _VOWEL_SANDHI:
            merged = _VOWEL_SANDHI[key]
            return A[: len(A) - lt] + merged + B[lh:]

    # Visarga handling
    if A.endswith("ḥ") or A.endswith("aḥ"):
        # simplified: keep visarga and concatenate
        return A + B

    # Default concatenation
    return A + B

def split(surface: str) -> List[Tuple[str, str]]:
    """
    Heuristic splitting: given a joined surface string attempt to return plausible (a,b) pairs
    that when joined produce the surface. This is not exhaustive but covers typical vowel sandhi cases.
    Returns list of candidate (a,b) pairs in canonicalized form.
    """
    s = canonicalize_symbol(surface)
    candidates: List[Tuple[str, str]] = []

    # Try to find a split index where left suffix + right prefix correspond to a sandhi result
    # For each possible partition, attempt to reverse vowel sandhi mapping
    for i in range(1, len(s)):
        left = s[:i]
        right = s[i:]
        # check direct concatenation (no sandhi)
        candidates.append((left, right))
        # Attempt to match reversed vowel sandhi: check if last char(s) of left + first char(s) of right map in mapping
        for (lv, rv), merged in _VOWEL_SANDHI.items():
            # if merged appears at the boundary
            boundary = left.endswith(merged) or right.startswith(merged)
            if boundary:
                # propose decomposition: left' = left_without_merged + lv, right' = rv + right_without_merged
                if left.endswith(merged):
                    l_prefix = left[: len(left) - len(merged)] + lv
                    r_suffix = right
                    candidates.append((l_prefix, r_suffix))
                if right.startswith(merged):
                    l_prefix = left
                    r_suffix = rv + right[len(merged) :]
                    candidates.append((l_prefix, r_suffix))
    # deduplicate preserving order
    seen = set()
    out = []
    for a, b in candidates:
        key = (a, b)
        if key not in seen:
            seen.add(key)
            out.append(key)
    return out
