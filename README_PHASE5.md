Phase 5: Morphological Disambiguator & Sandhi expansion (initial)

Added:
- src/sanskrit_nlp_core/disambig.py  (Viterbi-style disambiguator)
- src/sanskrit_nlp_core/sandhi_rules.py (expanded vowel sandhi mappings + reverse ranking)
- tests/test_disambig.py
- tests/test_sandhi_rules.py

Notes:
- Implementation is deterministic and conservative, intended as a baseline for
  future probabilistic or ML-based disambiguators.
- I will run tests and fix any issues if you want me to push and run CI; please
  confirm and I'll push the branch and monitor the Actions run.
