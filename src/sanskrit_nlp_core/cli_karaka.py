# coding: utf-8
import argparse
import sys
from .karaka import parse_sentence, render_ir

from .cli import main as previous_main  # keep previous CLI available


def main(argv=None):
    parser = argparse.ArgumentParser(prog="sanskrit-nlp-core-phase3", description="Phase 3 CLI: Karaka parser & IR")
    sub = parser.add_subparsers(dest="command", required=True)

    p_parse = sub.add_parser("karaka-parse", help="Parse a short sentence into Karaka IR")
    p_parse.add_argument("--text", required=True, help="Input sentence (English/Hinglish)")

    args = parser.parse_args(argv)

    if args.command == "karaka-parse":
        g = parse_sentence(args.text)
        print(render_ir(g))

if __name__ == "__main__":
    main()
