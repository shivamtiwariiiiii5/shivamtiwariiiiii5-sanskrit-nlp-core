# coding: utf-8
import pytest
from sanskrit_nlp_core.shiva import ShivaSutras
from sanskrit_nlp_core.phonetics import normalize_symbol

@pytest.fixture
def sutras():
    return ShivaSutras()

def test_linear_sequence_contains_it_markers(sutras):
    markers = sutras.it_markers()
    assert len(markers) == 14
    # every it marker should appear in the linear sequence
    seq = sutras.linear_sequence()
    for m in markers:
        assert m in seq

def test_pratyahara_ac_vowels(sutras):
    name, phonemes = sutras.form_pratyahara("a", "c")
    assert normalize_symbol(name) == normalize_symbol("ac")
    # ac corresponds to all vowels: a i u ṛ ḷ e o ai au  (depending on exact representation)
    # We assert a few canonical constituents are present in order
    assert phonemes[0] == normalize_symbol("a")
    # next should include i and u
    assert normalize_symbol("i") in phonemes
    assert normalize_symbol("u") in phonemes
    # ensure the it-marker 'c' is not included
    assert "c" not in phonemes

def test_pratyahara_ik(sutras):
    name, phonemes = sutras.form_pratyahara("i", "k")
    assert normalize_symbol(name) == normalize_symbol("ik")
    # i..k should include i, u, ṛ, ḷ
    expected = [normalize_symbol(x) for x in ("i", "u", "ṛ", "ḷ")]
    for e in expected:
        assert e in phonemes

def test_pratyahara_yaṇ(sutras):
    name, phonemes = sutras.form_pratyahara("y", "ṇ")
    assert normalize_symbol(name) == normalize_symbol("yṇ")
    # y..ṇ includes y, v, r, l (at least)
    for p in ("y", "v", "r", "l"):
        assert normalize_symbol(p) in phonemes

def test_invalid_it_marker(sutras):
    with pytest.raises(ValueError):
        sutras.form_pratyahara("a", "Z")  # invalid marker

def test_start_after_marker_invalid(sutras):
    # choose start near the end and it-marker earlier in the sequence
    with pytest.raises(ValueError):
        sutras.form_pratyahara("k", "ṇ")  # 'k' occurs after 'ṇ' in the sequence; invalid
