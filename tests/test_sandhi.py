# coding: utf-8
import pytest
from sanskrit_nlp_core.sandhi import join as sandhi_join, split as sandhi_split


def test_vowel_sandhi_a_i():
    out = sandhi_join("a", "i")
    assert out in ("e", "ayi", "ayi") or out.startswith("e")

def test_vowel_sandhi_a_a():
    out = sandhi_join("a", "a")
    assert out == "ā"

def test_split_simple():
    candidates = sandhi_split("e")
    # 'e' could be from a+i -> e; expect at least one candidate
    assert any(True for _ in candidates)
