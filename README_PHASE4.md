Phase 4: Paninian Rule Engine Database

This commit adds a lightweight Panini rule engine database and CLI to load/query
Panini sutra entries. It is intentionally small and demonstrative and includes a
sample data file data/panini_rules.json with a few entries.

Files added:
- src/sanskrit_nlp_core/panini.py
- data/panini_rules.json
- tests/test_panini.py
- src/sanskrit_nlp_core/cli_panini.py
- README_PHASE4.md

Usage examples:
- python -m sanskrit_nlp_core.cli_panini list-rules
- python -m sanskrit_nlp_core.cli_panini get-rule --id 1.1.71
- python -m sanskrit_nlp_core.cli_panini query-praty --praty ac
