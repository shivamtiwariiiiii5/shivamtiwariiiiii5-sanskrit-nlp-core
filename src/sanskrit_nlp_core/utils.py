# coding: utf-8
from typing import Iterable, List
from .phonetics import iast_to_devanagari, devanagari_to_iast, canonicalize_symbol

def tokens_to_devanagari(tokens: Iterable[str]) -> List[str]:
    return [iast_to_devanagari(t) for t in tokens]

def tokens_to_iast_from_devanagari(tokens: Iterable[str]) -> List[str]:
    return [devanagari_to_iast(t) for t in tokens]

def canonicalize_token(token: str) -> str:
    """
    Canonicalize any input token (ASCII/IAST/Devanagari) to IAST using phonetics.canonicalize_symbol.
    """
    return canonicalize_symbol(token)

def pretty_list(tokens: Iterable[str]) -> str:
    return ", ".join(tokens)
