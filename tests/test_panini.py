# coding: utf-8
import pytest
from sanskrit_nlp_core.panini import PaniniDB
import os

TEST_JSON = os.path.join(os.path.dirname(__file__), "..", "data", "panini_rules.json")


def test_load_rules():
    db = PaniniDB(json_path=TEST_JSON)
    all_rules = db.list_rules()
    assert len(all_rules) >= 3


def test_get_rule_by_id():
    db = PaniniDB(json_path=TEST_JSON)
    r = db.get_rule("1.1.71")
    assert r is not None
    assert r.id == "1.1.71"


def test_query_by_pratyahara_ac():
    db = PaniniDB(json_path=TEST_JSON)
    res = db.query_by_pratyahara("ac")
    # expecting at least the rule 1.1.71 and 1.1.72 to be returned
    ids = {r.id for r in res}
    assert "1.1.71" in ids
    assert "1.1.72" in ids
