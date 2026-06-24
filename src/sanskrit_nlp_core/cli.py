# coding: utf-8
import argparse
import sys
from .shiva import ShivaSutras
from .utils import tokens_to_devanagari, pretty_list

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

def main(argv=None):
    parser = argparse.ArgumentParser(prog="sanskrit-nlp-core", description="Phase 1 CLI for Shiva Sutras / pratyāhāra")
    sub = parser.add_subparsers(dest="command", required=True)

    p_praty = sub.add_parser("pratyahara", help="Form a pratyāhāra from start phoneme and it-marker")
    p_praty.add_argument("--start", required=True, help="Start phoneme (IAST)")
    p_praty.add_argument("--it", required=True, help="It-marker (IAST)")

    args = parser.parse_args(argv)
    if args.command == "pratyahara":
        cmd_pratyahara(args)

if __name__ == "__main__":
    main()
