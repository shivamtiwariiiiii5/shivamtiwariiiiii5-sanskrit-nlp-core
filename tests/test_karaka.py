# coding: utf-8
import pytest
from sanskrit_nlp_core.karaka import parse_sentence, render_ir


def test_parse_simple_subject_object():
    g = parse_sentence("Rama goes to the forest")
    # expecting a node for Rama and forest, and verb
    rendered = render_ir(g)
    assert "Rama" in rendered
    assert "forest" in rendered
    # check that verb has at least one outgoing edge
    assert any(True for e in g.edges if e.source in g.nodes)

def test_parse_subject_without_prep():
    g = parse_sentence("Hari eats rice")
    rendered = render_ir(g)
    assert "Hari" in rendered
    assert "rice" in rendered
    # karma edge present
    assert any(e.role == "karma" for e in g.edges)
