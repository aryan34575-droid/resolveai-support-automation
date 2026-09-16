from __future__ import annotations

import argparse
import json
import sys

from .pipeline import process_json


def main() -> int:
    parser = argparse.ArgumentParser(description="ResolveAI support ticket triage")
    parser.add_argument("--input", help="path to JSON; defaults to stdin")
    parser.add_argument("--approved", action="store_true", help="simulate explicit human approval")
    args = parser.parse_args()
    try:
        raw = open(args.input, encoding="utf-8").read() if args.input else sys.stdin.read()
        result = process_json(raw, approved=args.approved)
        print(json.dumps(result, indent=2))
        return 0 if result["status"] != "failed" else 1
    except OSError as exc:
        print(json.dumps({"status": "invalid", "errors": [str(exc)]}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
