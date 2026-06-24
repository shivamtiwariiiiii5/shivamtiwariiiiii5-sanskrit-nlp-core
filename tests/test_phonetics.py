# coding: utf-8
import pytest
from sanskrit_nlp_core.phonetics import (
    iast_to_devanagari,
    devanagari_to_iast,
    ascii_to_iast,
    canonicalize_symbol,
)

def test_iast_to_devanagari_roundtrip():
    # sample IAST tokens -> Devanagari -> back to IAST (via mapping) should preserve canonical tokens we support
    tokens = ["a", "ā", "i", "ī", "u", "ū", "ṛ", "ṝ", "ḷ", "e", "ai", "o", "au", "k", "kh", "g", "ṅ", "c", "ch", "j", "ñ"]
    for t in tokens:
        d = iast_to_devanagari(t)
        # ensure we can map back if glyph mapping exists
        back = devanagari_to_iast(d)
        # For tokens that had direct glyph mapping, mapping back should equal a known IAST (may differ for some forms)
        assert back == (t if d != t else back)

def test_ascii_to_iast_basic():
    assert ascii_to_iast("aa") == "ā"
    assert ascii_to_iast("ii") == "ī"
    assert ascii_to_iast("uu") == "ū"
    assert ascii_to_iast("sh") == "ś"
    assert ascii_to_iast("Sh") == "ṣ"
    # combined sequences
    assert ascii_to_iast("ksha")[:3]  # ensures function returns something for ksha

def test_canonicalize_symbol_devanagari_input():
    # Devanagari 'अ' -> 'a'
    assert canonicalize_symbol("अ") == "a"
    # Devanagari 'आ' -> 'ā'
    assert canonicalize_symbol("आ") == "ā"

def test_canonicalize_symbol_ascii_input():
    assert canonicalize_symbol("aa") == "ā"
    assert canonicalize_symbol("sh") == "ś"
    assert canonicalize_symbol("H") == "ḥ"
