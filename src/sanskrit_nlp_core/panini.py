from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import json
import os

from .shiva import ShivaSutras

@dataclass
class PaniniRule:
    id: str
    sutra: str
    text: str
    pratyahara: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    notes: Optional[str] = None

class PaniniDB:
    """
    Lightweight Panini Rule Engine Database loader and query API.
    - Loads rules from a JSON file containing PaniniRule records.
    - Supports queries by rule id, by tag, and by pratyahara name.

    This is intentionally simple and designed for Phase 4 to provide an
    extendable bridge to a fuller rule engine later.
    """
    def __init__(self, json_path: str = None):
        self.rules: Dict[str, PaniniRule] = {}
        self.shiva = ShivaSutras()
        if json_path:
            self.load_from_json(json_path)

    def load_from_json(self, json_path: str):
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Rules file not found: {json_path}")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for entry in data:
            praty = entry.get("pratyahara", [])
            rule = PaniniRule(
                id=entry["id"], sutra=entry.get("sutra", ""), text=entry.get("text", ""),
                pratyahara=praty, tags=entry.get("tags", []), notes=entry.get("notes"),
            )
            self.rules[rule.id] = rule

    def get_rule(self, rule_id: str) -> Optional[PaniniRule]:
        return self.rules.get(rule_id)

    def list_rules(self) -> List[PaniniRule]:
        return list(self.rules.values())

    def query_by_tag(self, tag: str) -> List[PaniniRule]:
        return [r for r in self.rules.values() if tag in r.tags]

    def query_by_pratyahara(self, praty: str) -> List[PaniniRule]:
        """
        Return rules that explicitly list the given pratyahara name.
        Also supports querying by derived phoneme set: if praty is a pratyahara name like 'ac', it will
        compute its phoneme set and return rules that reference any of those phonemes in their tags.
        """
        norm = praty.strip()
        matched: List[PaniniRule] = []
        # direct matches
        for r in self.rules.values():
            if norm in r.pratyahara:
                matched.append(r)
        # If praty corresponds to a real pratyahara via ShivaSutras, expand
        try:
            name, phonemes = self.shiva.form_pratyahara(norm[0], norm[1]) if len(norm) >= 2 else (None, [])
        except Exception:
            phonemes = []
        # match phonemes in tags or notes (simple heuristic)
        for r in self.rules.values():
            for p in phonemes:
                if p in r.tags or (r.notes and p in r.notes):
                    if r not in matched:
                        matched.append(r)
        return matched

    def add_rule(self, rule: PaniniRule):
        if rule.id in self.rules:
            raise KeyError(f"Rule with id {rule.id} already exists")
        self.rules[rule.id] = rule

    def save_to_json(self, json_path: str):
        data = []
        for r in self.rules.values():
            data.append({
                "id": r.id,
                "sutra": r.sutra,
                "text": r.text,
                "pratyahara": r.pratyahara,
                "tags": r.tags,
                "notes": r.notes,
            })
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
