# coding: utf-8
"""
Morphological analyzer for Phase 2.
Provides a light-weight, deterministic morphological analyzer tailored for Sanskrit
using a lexicon + affix inventory and leveraging Phase 1 canonicalization utilities.

Features:
- Small lexicon of roots/stems with POS and morph features
- Affix inventory (common nominal case endings, verb endings)
- Analyzer that attempts longest-match affix stripping and returns analyses

This module is intentionally self-contained and production-grade for Phase 2 scope.
"""
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass

from .phonetics import canonicalize_symbol

@dataclass(frozen=True)
class Lexeme:
    lemma: str
    pos: str
    gloss: str = ""
    features: Dict[str, Any] = None

@dataclass
class Analysis:
    surface: str
    lemma: str
    pos: str
    stem: str
    affix: str
    features: Dict[str, Any]

# Minimal lexicon (IAST canonical forms)
_LEXICON: Dict[str, Lexeme] = {
    "rama": Lexeme(lemma="rama", pos="noun", gloss="Rama (proper name)", features={"gender": "m"}),
    "hari": Lexeme(lemma="hari", pos="noun", gloss="Vishnu/Hari", features={"gender": "m"}),
    "gacch": Lexeme(lemma="gacch", pos="verb", gloss="go", features={"root": True}),
    "bhu": Lexeme(lemma="bhu", pos="verb", gloss="become/earth", features={"root": True}),
    "pa": Lexeme(lemma="pa", pos="verb", gloss="protect/feed", features={"root": True}),
}

# Common nominal suffixes (simplified) mapping surface->feature map
# Ordered longest-first for deterministic stripping
_NOMINAL_AFFIXES: List[Tuple[str, Dict[str, str]]] = [
    ("āḥ", {"case": "nom_pl", "ending": "āḥ"}),
    ("au", {"case": "nom_du", "ending": "au"}),
    ("am", {"case": "acc_sg", "ending": "am"}),
    ("ā", {"case": "nom_sg_f", "ending": "ā"}),
    ("aḥ", {"case": "nom_sg_m_visarga", "ending": "aḥ"}),
    ("a", {"case": "nom_sg_m", "ending": "a"}),
    ("i", {"case": "nom_sg_i", "ending": "i"}),
]

# Common verbal endings (very simplified)
_VERBAL_AFFIXES: List[Tuple[str, Dict[str, str]]] = [
    ("anti", {"person": "3", "number": "pl"}),
    ("ati", {"person": "3", "number": "sg"}),
    ("asi", {"person": "2", "number": "sg"}),
    ("mi", {"person": "1", "number": "sg"}),
]

# Combined affix list ordered for search
_AFFIXES = _NOMINAL_AFFIXES + _VERBAL_AFFIXES

def analyze_token(token: str, max_results: int = 10) -> List[Analysis]:
    """
    Analyze a surface token and return possible analyses.
    Strategy:
      - Canonicalize input (IAST)
      - Try exact lexicon match
      - Else try longest affix stripping using _AFFIXES; check resulting stem in lexicon
      - If stem not in lexicon, still return stem+affix as unknown lemma candidate
    """
    tok = canonicalize_symbol(token)
    results: List[Analysis] = []

    # Exact lexicon match
    if tok in _LEXICON:
        lex = _LEXICON[tok]
        results.append(Analysis(surface=tok, lemma=lex.lemma, pos=lex.pos, stem=tok, affix="", features=lex.features or {}))

    # Affix stripping
    for aff, feats in _AFFIXES:
        if tok.endswith(aff):
            stem = tok[: len(tok) - len(aff)]
            # if stem is empty try to skip
            if not stem:
                continue
            # look up stem in lexicon
            if stem in _LEXICON:
                lex = _LEXICON[stem]
                merged = dict(lex.features or {})
                merged.update(feats)
                results.append(Analysis(surface=tok, lemma=lex.lemma, pos=lex.pos, stem=stem, affix=aff, features=merged))
            else:
                # Unknown stem: still produce an analysis candidate
                results.append(Analysis(surface=tok, lemma=stem, pos="unknown", stem=stem, affix=aff, features=feats.copy()))
        # early exit if too many
        if len(results) >= max_results:
            break

    # If no analysis found, produce fallback best-effort segmentation: try all split points
    if not results:
        for i in range(1, len(tok)):
            stem = tok[:i]
            aff = tok[i:]
            results.append(Analysis(surface=tok, lemma=stem, pos="unknown", stem=stem, affix=aff, features={}))
            if len(results) >= max_results:
                break

    return results

# Public small utility to add lexicon entries (useful in Phase 2+)
def add_lexeme(lex: Lexeme):
    key = canonicalize_symbol(lex.lemma)
    _LEXICON[key] = lex

# Small example: expose inventory listing
def list_lexicon() -> Dict[str, Lexeme]:
    return dict(_LEXICON)
