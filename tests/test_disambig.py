# coding: utf-8
import pytest
from sanskrit_nlp_core.disambig import disambiguate_tokens


def test_disambiguate_basic():
    toks = ["Rama", "gacchati"]
    seq = disambiguate_tokens(toks)
    # Expect two analyses returned
    assert len(seq) == 2
    # The lemma for first token should be 'rama' (canonicalized)
    assert any(getattr(a, 'lemma', '').startswith('rama') for a in seq)

