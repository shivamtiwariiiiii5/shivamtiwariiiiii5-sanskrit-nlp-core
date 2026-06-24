# coding: utf-8
"""
Morphological disambiguator (Phase 5)

This module implements a lightweight, deterministic disambiguation algorithm over
sequences of token analyses produced by Phase 2 morphology. It uses a simple
Viterbi-like dynamic programming approach with heuristic scoring functions to
prefer lexicon matches, plausible POS sequences, and Panini-derived priors.

APIs:
 - disambiguate_tokens(tokens: List[str]) -> List[Analysis]
 - score_analysis(prev_analysis, analysis, position, token_sequence) -> float

The implementation is intentionally conservative and easy to extend.
"""
from typing import List, Optional, Tuple, Dict
from collections import defaultdict

from .morphology import analyze_token, Analysis
from .panini import PaniniDB
from .phonetics import canonicalize_symbol

# Small transition preferences (prev_pos -> curr_pos) -> score bonus
_TRANSITION_BONUSES = {
    ("noun", "verb"): 3.0,
    ("pronoun", "verb"): 3.0,
    ("verb", "noun"): 1.0,
    ("verb", "adp"): 1.5,  # preposition after verb possible in some constructions
}

# Penalties
_UNKNOWN_POS_PENALTY = -2.0
_AFFIX_PENALTY = -0.5
_EXACT_LEXICON_BONUS = 2.0


class Disambiguator:
    def __init__(self, panini_db: Optional[PaniniDB] = None):
        self.panini = panini_db or PaniniDB()

    def _score(self, prev: Optional[Analysis], cur: Analysis, position: int, tokens: List[str]) -> float:
        """Heuristic score for a single analysis given previous analysis and context."""
        score = 0.0
        # Prefer exact lexicon/stem matches (affix empty)
        if getattr(cur, "affix", None) == "" or getattr(cur, "affix", None) is None:
            score += _EXACT_LEXICON_BONUS
        else:
            # small penalty for having affix (i.e., inflected form)
            score += _AFFIX_PENALTY

        # POS-based priors
        pos = getattr(cur, "pos", "unknown")
        if pos == "unknown":
            score += _UNKNOWN_POS_PENALTY

        # transition bonuses from previous POS
        if prev:
            prev_pos = getattr(prev, "pos", "unknown")
            bonus = _TRANSITION_BONUSES.get((prev_pos, pos), 0.0)
            score += bonus

        # small heuristic: if token is capitalized (likely proper noun), prefer noun analyses
        tok = tokens[position]
        if tok and tok[0].isupper() and pos == "noun":
            score += 1.5

        # Panini priors: if analysis features mention items appearing in panini rules tags, give tiny bonus
        if self.panini:
            # check if any feature key or value matches known panini rule tags
            for r in self.panini.list_rules():
                for tag in r.tags:
                    if tag in (pos, cur.lemma):
                        score += 0.5

        return score

    def disambiguate_tokens(self, tokens: List[str]) -> List[Analysis]:
        """
        Disambiguate a sequence of surface tokens. Returns the best analysis sequence.
        Uses dynamic programming (Viterbi-like) across candidate analyses from analyze_token.
        """
        n = len(tokens)
        if n == 0:
            return []

        # candidates[i] = list of analyses for token i
        candidates: List[List[Analysis]] = []
        for tok in tokens:
            can = canonicalize_symbol(tok)
            analyses = analyze_token(can, max_results=8)
            candidates.append(analyses)

        # dp[i][j] = (best_score, prev_index)
        dp: List[List[Tuple[float, Optional[int]]]] = [ [(float("-inf"), None) for _ in cand] for cand in candidates ]

        # initialize
        for j, a in enumerate(candidates[0]):
            dp[0][j] = (self._score(None, a, 0, tokens), None)

        # fill
        for i in range(1, n):
            for j, cur in enumerate(candidates[i]):
                best_score = float("-inf")
                best_prev = None
                for k, prev in enumerate(candidates[i-1]):
                    prev_score, _ = dp[i-1][k]
                    if prev_score == float("-inf"):
                        continue
                    s = prev_score + self._score(prev, cur, i, tokens)
                    if s > best_score:
                        best_score = s
                        best_prev = k
                dp[i][j] = (best_score, best_prev)

        # backtrack best final
        best_final_score = float("-inf")
        best_final_idx = None
        for j, (score, prev_idx) in enumerate(dp[-1]):
            if score > best_final_score:
                best_final_score = score
                best_final_idx = j

        if best_final_idx is None:
            # fallback: pick first analysis of each token
            return [cand[0] for cand in candidates]

        # reconstruct
        seq: List[Analysis] = [None] * n
        idx = best_final_idx
        for i in range(n-1, -1, -1):
            seq[i] = candidates[i][idx]
            _, prev_idx = dp[i][idx]
            idx = prev_idx if prev_idx is not None else 0

        return seq


# Convenience function
_default_disamb = Disambiguator()

def disambiguate_tokens(tokens: List[str]) -> List[Analysis]:
    return _default_disamb.disambiguate_tokens(tokens)
