Updated README: Phase 2 added

Phase 2 deliverables:
- Morphological Analyzer (lexicon + affix-based analyzer)
- Sandhi Engine (joining and heuristic splitting)
- CLI commands: analyze, list-lexicon, sandhi-join, sandhi-split

Usage (examples):
- python -m sanskrit_nlp_core.cli analyze --token ramaḥ
- python -m sanskrit_nlp_core.cli sandhi-join --left a --right i
- python -m sanskrit_nlp_core.cli sandhi-split --surface e
