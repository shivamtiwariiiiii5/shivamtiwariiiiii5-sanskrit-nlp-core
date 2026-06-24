Phase 3: Karaka Parser & Semantic Dependency Graph

This commit adds:
- src/sanskrit_nlp_core/karaka.py : deterministic Karaka parser producing IRGraph
- tests/test_karaka.py : unit tests for simple parsing scenarios
- src/sanskrit_nlp_core/cli_karaka.py : small CLI wrapper to run karaka parsing from command line

Usage:
- python -m sanskrit_nlp_core.cli_karaka karaka-parse --text "Rama goes to the forest"

Design notes:
- The parser uses conservative heuristics and a small English->Sanskrit verb lexicon.
- It integrates with Phase1/Phase2 utilities (canonicalize_symbol, analyze_token) for token normalization.
