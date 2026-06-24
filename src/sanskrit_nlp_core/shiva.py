# coding: utf-8
from typing import List, Tuple, Dict, Sequence
from dataclasses import dataclass

from .phonetics import normalize_symbol

@dataclass(frozen=True)
class Sutra:
    tokens: Tuple[str, ...]
    it_marker: str

    @property
    def phonemes(self) -> Tuple[str, ...]:
        # All tokens except the last (it marker)
        return tuple(self.tokens[:-1])

class ShivaSutras:
    """
    Canonical representation of the 14 Shiva Sūtras (Maheshvara Sūtras).
    Each sutra is tokenized; the final token is the 'it' marker (not part of the phoneme set).
    Methods:
      - linear_sequence(): returns the concatenation of all tokens (including it-markers) as a list.
      - form_pratyahara(start, it_marker): returns (pratyahara_name, phoneme_list)
    """

    # Represent sutras in IAST (Unicode) tokens; the final token in each list is the it-marker.
    _raw_sutras: Sequence[Tuple[str, ...]] = (
        ("a", "i", "u", "ṇ"),                       # 1: a i u ṇ
        ("ṛ", "ḷ", "k"),                            # 2: ṛ ḷ k
        ("e", "o", "ṅ"),                            # 3: e o ṅ
        ("ai", "au", "c"),                          # 4: ai au c
        ("h", "y", "v", "r", "ṭ"),                  # 5: h y v r ṭ
        ("l", "ṇ"),                                 # 6: l ṇ
        ("ñ", "m", "ṅ", "ṇ", "n", "m̐"),            # 7: ñ m ṅ ṇ n m̐  (m̐ / anusvāra used to mark)
        ("jha", "bha", "ñ̇"),                       # 8: jha bha ñ (marker uses diacritic here)
        ("gha", "ḍha", "dha", "ṣ"),                 # 9: gha ḍha dha ṣ
        ("ja", "ba", "ga", "ḍa", "da", "ś"),        # 10: ja ba ga ḍa da ś
        ("kha", "pha", "cha", "ṭha", "tha", "ca", "ṭa", "ta", "v̇"),  # 11
        ("ka", "pa", "y"),                          # 12: ka pa y
        ("śa", "ṣa", "sa", "r̥"),                   # 13: śa ṣa sa r (r-mark here r̥ to avoid confusion)
        ("ha", "l̥"),                                # 14: ha l (l̥ used as marker symbol)
    )

    def __init__(self):
        # Normalize tokens (e.g., canonical combining marks).
        sutras: List[Sutra] = []
        for tokens in self._raw_sutras:
            norm_tokens = tuple(normalize_symbol(t) for t in tokens)
            sutras.append(Sutra(tokens=norm_tokens, it_marker=norm_tokens[-1]))
        self.sutras: Tuple[Sutra, ...] = tuple(sutras)

    def linear_sequence(self) -> List[str]:
        """
        Return the linear concatenation of all tokens, preserving order, including it-markers.
        """
        seq: List[str] = []
        for s in self.sutras:
            seq.extend(list(s.tokens))
        return seq

    def it_markers(self) -> List[str]:
        """Return the canonical list of it-markers (one per sutra)."""
        return [s.it_marker for s in self.sutras]

    def phoneme_inventory(self) -> List[str]:
        """Return the ordered list of phonemes (all tokens except it-markers) in linear order."""
        phonemes: List[str] = []
        for s in self.sutras:
            phonemes.extend(list(s.phonemes))
        return phonemes

    def find_first_occurrence(self, symbol: str) -> int:
        """
        Find the first index of symbol in the linear sequence.
        Raises ValueError if not found.
        """
        seq = self.linear_sequence()
        norm = normalize_symbol(symbol)
        for i, tok in enumerate(seq):
            if tok == norm:
                return i
        raise ValueError(f"Symbol '{symbol}' not found in Shiva Sūtras linear sequence.")

    def form_pratyahara(self, start: str, it_marker: str) -> Tuple[str, List[str]]:
        """
        Form a pratyāhāra given a start phoneme and an it-marker.
        Returns (name, phoneme_list) where name is start+it_marker.
        Algorithm:
          - Build linear sequence of tokens (including it-markers).
          - Find index of the first occurrence of start token.
          - Find index of the (it_marker) token which must be an it-marker present as the last token of a sutra.
          - The set is seq[start_index : it_index] (it excluded).
        """
        seq = self.linear_sequence()
        start_norm = normalize_symbol(start)
        it_norm = normalize_symbol(it_marker)

        # Validate it_marker is an it marker (must appear as sutra.it_marker)
        markers = self.it_markers()
        if it_norm not in markers:
            raise ValueError(f"'{it_marker}' is not a recognized it-marker for the canonical 14 Shiva Sūtras.")

        # Locate positions
        try:
            start_idx = seq.index(start_norm)
        except ValueError:
            raise ValueError(f"Start symbol '{start}' not found in Shiva Sūtras linear sequence.")

        # Find the index of the marker token (first occurrence)
        try:
            it_idx = seq.index(it_norm)
        except ValueError:
            # Defensive: should not happen if marker validation passed
            raise ValueError(f"It-marker '{it_marker}' not found in Shiva Sūtras linear sequence.")

        if start_idx >= it_idx:
            raise ValueError(
                f"Invalid pratyāhāra: start symbol '{start}' occurs at or after the it-marker '{it_marker}' in the canonical ordering."
            )

        phoneme_slice = seq[start_idx:it_idx]
        pratyahara_name = f"{start_norm}{it_norm}"
        return pratyahara_name, phoneme_slice
