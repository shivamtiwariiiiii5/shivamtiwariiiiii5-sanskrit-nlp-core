# coding: utf-8
"""
Additional sandhi rules and utilities (Phase 5 expansion)

This module provides a slightly expanded list of vowel/consonant sandhi rules
and utilities to rank reverse-sandhi candidates. It's intentionally small for
Phase 5 but designed to be extended.
"""
from typing import List, Tuple

# Expanded vowel sandhi mapping for joining: (left, right) -> result
VOWEL_SANDHI_EXPANDED = {
    ("a", "a"): "ā",
    ("a", "i"): "e",
    ("a", "ī"): "e",
    ("a", "u"): "o",
    ("a", "ū"): "o",
    ("i", "a"): "ya",
    ("ī", "a"): "yā",
    ("u", "a"): "va",
    ("e", "a"): "aya",
    ("o", "a"): "ava",
    ("a", "ai"): "ai",
    ("a", "au"): "au",
}

# For reverse-sandhi ranking: given a joined string at a boundary, prefer decompositions
# that involve shorter replacements and frequently observed outcomes.

REVERSE_PRIORITY = ["ā", "e", "o", "ai", "au", "ya", "va", "aya", "ava"]


def rank_reverse_candidates(joined_fragment: str) -> List[Tuple[str, str]]:
    """
    Given a joined fragment (e.g., "e"), return a ranked list of (left_vowel, right_vowel)
    candidates that could have produced it.
    """
    out: List[Tuple[str, str]] = []
    for (l, r), merged in VOWEL_SANDHI_EXPANDED.items():
        if merged == joined_fragment:
            out.append((l, r))
    # sort by REVERSE_PRIORITY on merged form index
    out.sort(key=lambda pair: REVERSE_PRIORITY.index(VOWEL_SANDHI_EXPANDED.get(pair, "zz")) if VOWEL_SANDHI_EXPANDED.get(pair, "zz") in REVERSE_PRIORITY else 999)
    return out
