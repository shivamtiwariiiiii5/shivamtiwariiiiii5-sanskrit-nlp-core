# coding: utf-8
"""
Karaka Parser & Semantic Dependency Graph (Phase 3)

This module provides a deterministic, rule-based mapper that converts short English/Hinglish
input sentences into a Sanskrit-structured Intermediate Representation (IR) using Panini-style
karaka roles. The implementation is intentionally conservative and deterministic to provide
a solid baseline for further expansion in later phases.

Key APIs:
 - parse_sentence(text, language='en') -> IRGraph
 - IRGraph/IRNode dataclasses for serializing and inspection

Design notes:
 - Uses Phase 1 canonicalization utilities and Phase 2 morphology to normalize tokens.
 - Verb detection uses a small English->Sanskrit verb lexicon for mapping.
 - Karaka role assignment follows simple syntactic heuristics (prepositions, word order).
"""
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any
import itertools
import re

from .phonetics import canonicalize_symbol
from .morphology import analyze_token

# Define Karaka roles (a small set for the initial IR)
KARAKA_ROLES = ("kartA", "karma", "karana", "samprAdAna", "adhikara", "apadana", "adhyApana", "location")

@dataclass
class IRNode:
    id: int
    token: str
    lemma: str
    pos: str
    features: Dict[str, Any] = field(default_factory=dict)

@dataclass
class IREdge:
    source: int
    target: int
    role: str

@dataclass
class IRGraph:
    nodes: Dict[int, IRNode] = field(default_factory=dict)
    edges: List[IREdge] = field(default_factory=list)

    def add_node(self, token: str, lemma: str, pos: str, features: Dict[str, Any] = None) -> int:
        node_id = (max(self.nodes.keys()) + 1) if self.nodes else 1
        self.nodes[node_id] = IRNode(id=node_id, token=token, lemma=lemma, pos=pos, features=features or {})
        return node_id

    def add_edge(self, source: int, target: int, role: str):
        if role not in KARAKA_ROLES:
            # allow unknown role but keep it as-is
            pass
        self.edges.append(IREdge(source=source, target=target, role=role))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": {nid: vars(n) for nid, n in self.nodes.items()},
            "edges": [vars(e) for e in self.edges],
        }

# Small English->Sanskrit verb lexicon for verb detection
_EN_TO_SANSKRIT_VERBS = {
    "go": "gacch",
    "goes": "gacch",
    "went": "gacch",
    "walk": "gacch",
    "walks": "gacch",
    "see": "pa",
    "sees": "pa",
    "eat": "khad",
    "eats": "khad",
    "run": "i",  # placeholder root
    "sleep": "ni",
}

# Prepositions -> karaka mapping heuristics
_PREPOSITION_ROLE = {
    "to": "adhikara",      # goal/destination
    "into": "adhikara",
    "in": "location",
    "on": "location",
    "at": "location",
    "with": "karana",
    "by": "karana",
    "for": "samprAdAna",
}

WORD_SPLIT_RE = re.compile(r"\s+")

def _is_verb_token(tok: str) -> bool:
    t = tok.lower()
    return t in _EN_TO_SANSKRIT_VERBS

def _map_verb(tok: str) -> str:
    return _EN_TO_SANSKRIT_VERBS.get(tok.lower(), tok)

def parse_sentence(text: str, language: str = "en") -> IRGraph:
    """
    Parse a short sentence in English/Hinglish into an IRGraph with karaka roles.

    Algorithm (deterministic heuristics):
      - Tokenize on whitespace and punctuation
      - Identify the main verb token by matching small verb lexicon
      - Tokens before verb -> candidate subject (kartA)
      - Tokens after verb -> candidate objects; prepositions modify role assignment
      - For each token, call analyze_token() to get lemma and POS hints; use first analysis
      - Build nodes for each significant token and edges with assigned roles

    This is intentionally conservative and intended as a starting point for robust parsing.
    """
    text = text.strip()
    # basic tokenization: split on whitespace and strip punctuation
    raw_tokens = [t.strip(".,!?;()[]") for t in WORD_SPLIT_RE.split(text) if t.strip()]
    tokens = raw_tokens

    graph = IRGraph()

    # find verb index
    verb_idx = None
    for i, tok in enumerate(tokens):
        if _is_verb_token(tok):
            verb_idx = i
            break
    # fallback: if no verb found, pick first verb-like (ends with 's' or common 'ed')
    if verb_idx is None:
        for i, tok in enumerate(tokens):
            if tok.lower().endswith("s") or tok.lower().endswith("ed"):
                verb_idx = i
                break

    # If still none, assume second token as verb if length >=3 else middle
    if verb_idx is None:
        verb_idx = 1 if len(tokens) > 1 else 0

    # Create nodes and store them
    node_ids: List[int] = []
    analyses_cache: Dict[int, List[Any]] = {}
    for i, tok in enumerate(tokens):
        can = canonicalize_symbol(tok)
        analyses = analyze_token(can)
        analyses_cache[i] = analyses
        # pick best analysis heuristically (exact lexicon match preferred)
        best = analyses[0]
        nid = graph.add_node(token=tok, lemma=best.lemma, pos=best.pos, features=best.features)
        node_ids.append(nid)

    # Determine subject (tokens before verb)
    subject_nodes = node_ids[:verb_idx]
    if subject_nodes:
        # prefer last token before verb as head of subject
        subj_head = subject_nodes[-1]
    else:
        subj_head = node_ids[0] if node_ids else None

    # Verb node
    verb_node = node_ids[verb_idx]

    # assign kartA edge from verb to subject
    if subj_head is not None:
        graph.add_edge(source=verb_node, target=subj_head, role="kartA")

    # Process tokens after verb for objects and prepositional roles
    i = verb_idx + 1
    while i < len(tokens):
        tok = tokens[i]
        lower = tok.lower()
        if lower in _PREPOSITION_ROLE and i + 1 < len(tokens):
            role = _PREPOSITION_ROLE[lower]
            target_node = node_ids[i + 1]
            graph.add_edge(source=verb_node, target=target_node, role=role)
            i += 2
            continue
        else:
            # default: object (karma)
            target_node = node_ids[i]
            graph.add_edge(source=verb_node, target=target_node, role="karma")
            i += 1

    return graph

# Small convenience: pretty print
def render_ir(graph: IRGraph) -> str:
    lines = []
    for nid, node in graph.nodes.items():
        lines.append(f"{nid}: {node.token} (lemma={node.lemma}, pos={node.pos})")
    lines.append("Edges:")
    for e in graph.edges:
        lines.append(f"{e.source} -[{e.role}]-> {e.target}")
    return "\n".join(lines)
