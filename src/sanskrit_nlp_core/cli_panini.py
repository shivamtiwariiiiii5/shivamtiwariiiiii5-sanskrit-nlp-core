# coding: utf-8
import argparse
import sys
import os
from .panini import PaniniDB

DEFAULT_RULES = os.path.join(os.path.dirname(__file__), "..", "data", "panini_rules.json")

def main(argv=None):
    parser = argparse.ArgumentParser(prog="sanskrit-nlp-core-panini", description="Panini Rule Engine CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list-rules", help="List all loaded rules")
    p_list.add_argument("--path", default=DEFAULT_RULES)

    p_get = sub.add_parser("get-rule", help="Get a rule by id")
    p_get.add_argument("--id", required=True)
    p_get.add_argument("--path", default=DEFAULT_RULES)

    p_q = sub.add_parser("query-praty", help="Query rules by pratyahara name")
    p_q.add_argument("--praty", required=True)
    p_q.add_argument("--path", default=DEFAULT_RULES)

    args = parser.parse_args(argv)

    db = PaniniDB(json_path=args.path)

    if args.command == "list-rules":
        for r in db.list_rules():
            print(f"{r.id}: {r.sutra} ({', '.join(r.tags)})")
    elif args.command == "get-rule":
        r = db.get_rule(args.id)
        if not r:
            print("Rule not found", file=sys.stderr)
            sys.exit(2)
        print(f"{r.id}: {r.sutra}\n{r.text}\nPratyahara: {r.pratyahara}\nTags: {r.tags}\nNotes: {r.notes}")
    elif args.command == "query-praty":
        res = db.query_by_pratyahara(args.praty)
        for r in res:
            print(f"{r.id}: {r.sutra} ({', '.join(r.tags)})")

if __name__ == "__main__":
    main()
