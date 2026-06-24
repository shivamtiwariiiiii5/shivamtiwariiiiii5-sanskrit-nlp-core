# coding: utf-8
import argparse
import sys
from .shiva import ShivaSutras
from .utils import tokens_to_devanagari, pretty_list, canonicalize_token
from .morphology import analyze_token, list_lexicon
from .sandhi import join as sandhi_join, split as sandhi_split

def cmd_pratyahara(args):
    sutras = ShivaSutras()
    try:
        name, phonemes = sutras.form_pratyahara(args.start, args.it)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

    dev = tokens_to_devanagari(phonemes)
    print(f"Pratyāhāra name: {name}")
    print("Phonemes (IAST):")
    print(pretty_list(phonemes))
    print()
    print("Phonemes (Devanagari):")
    print(pretty_list(dev))

def cmd_analyze(args):
    token = canonicalize_token(args.token)
    analyses = analyze_token(token)
    for a in analyses:
        print(f"Surface: {a.surface}  Lemma: {a.lemma}  POS: {a.pos}  Stem: {a.stem}  Affix: {a.affix}  Features: {a.features}")

def cmd_list_lexicon(args):
    lex = list_lexicon()
    for k, v in lex.items():
        print(f"{k}\t-> {v.pos} [{v.gloss}] features={v.features}")

def cmd_sandhi_join(args):
    out = sandhi_join(args.left, args.right)
    print(out)

def cmd_sandhi_split(args):
    out = sandhi_split(args.surface)
    for a, b in out:
        print(f"{a} + {b}")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="sanskrit-nlp-core", description="Phase 1+2 CLI for Sanskrit core tools")
    sub = parser.add_subparsers(dest="command", required=True)

    p_praty = sub.add_parser("pratyahara", help="Form a pratyāhāra from start phoneme and it-marker")
    p_praty.add_argument("--start", required=True, help="Start phoneme (IAST)")
    p_praty.add_argument("--it", required=True, help="It-marker (IAST)")

    p_an = sub.add_parser("analyze", help="Morphological analyze a token")
    p_an.add_argument("--token", required=True, help="Token to analyze (ASCII/IAST/Devanagari)")

    p_list = sub.add_parser("list-lexicon", help="List lexicon entries")

    p_join = sub.add_parser("sandhi-join", help="Apply sandhi join on two tokens")
    p_join.add_argument("--left", required=True)
    p_join.add_argument("--right", required=True)

    p_split = sub.add_parser("sandhi-split", help="Heuristic sandhi split a joined surface")
    p_split.add_argument("--surface", required=True)

    args = parser.parse_args(argv)
    if args.command == "pratyahara":
        cmd_pratyahara(args)
    elif args.command == "analyze":
        cmd_analyze(args)
    elif args.command == "list-lexicon":
        cmd_list_lexicon(args)
    elif args.command == "sandhi-join":
        cmd_sandhi_join(args)
    elif args.command == "sandhi-split":
        cmd_sandhi_split(args)

if __name__ == "__main__":
    main()
