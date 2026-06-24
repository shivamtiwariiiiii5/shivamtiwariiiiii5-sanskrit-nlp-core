# coding: utf-8
import pytest
from sanskrit_nlp_core.morphology import analyze_token, add_lexeme, list_lexicon
from sanskrit_nlp_core.phonetics import canonicalize_symbol


def test_analyze_exact_lexicon():
    analyses = analyze_token("rama")
    assert any(a.lemma == "rama" and a.pos == "noun" for a in analyses)

def test_analyze_with_affix():
    # 'rama' + 'aḥ' -> 'ramaḥ' (nom sg m with visarga) - our analyzer will detect 'aḥ' as affix when input matches
    analyses = analyze_token("ramaḥ")
    assert any(a.stem == canonicalize_symbol("rama") for a in analyses)

def test_add_lexeme_and_list():
    add_lexeme(type("L", (), {"lemma": "testroot", "pos": "noun", "gloss": "t", "features": {}})())
    lex = list_lexicon()
    assert "testroot" in lex
