# coding: utf-8
import pytest
from sanskrit_nlp_core.sandhi_rules import rank_reverse_candidates


def test_rank_reverse_candidates_e():
    cands = rank_reverse_candidates('e')
    # expect at least ('a','i') or ('a','ī') in candidates
    assert any(pair == ('a','i') or pair == ('a','ī') for pair in cands)
