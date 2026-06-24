# Sanskrit-Powered Core NLP & Logical AI Engine — Phase 1

Phase 1 deliverables:
- Project scaffolding (src package, tests, CLI).
- Implementation of canonical 14 Śiva Sūtras (Maheshvara Sūtras) with it-markers.
- Deterministic pratyāhāra generator.
- Basic phonetic inventory and transliteration helpers (IAST <-> Devanagari for sutra phonemes).
- Unit tests (pytest).

Usage:
- Install dependencies: `pip install -e .`
- Run tests: `pytest -q`
- CLI example: `python -m sanskrit_nlp_core.cli pratyahara --start a --it c`

Design notes:
- The Shiva Sūtras are represented in canonical order; each sutra is tokenized and the last token is treated as the it-marker.
- Pratyāhāra generation builds a linear sequence (including it-markers) and slices from the first occurrence of the start phoneme to the it-marker (exclusive).
- Transliteration utilities are intentionally conservative and cover the set of phonemes present in the sutras for robustness in Phase 1.

Next: upon "APPROVED PHASE 1" I will proceed to Phase 2 (Morphological Analyzer & Sandhi Engine).
