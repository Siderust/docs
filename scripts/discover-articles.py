#!/usr/bin/env python3
"""Print the JSON matrix of independently buildable LaTeX articles."""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / "articles"


def discover():
    if not ARTICLES.is_dir():
        raise SystemExit("Missing articles/ directory")
    found = []
    for directory in sorted(ARTICLES.iterdir()):
        if directory.is_symlink():
            raise SystemExit(f"Article must not be a symlink: {directory.name}")
        if not directory.is_dir():
            continue
        if re.fullmatch(r"[a-z][a-z0-9-]*", directory.name) is None:
            raise SystemExit(f"Invalid article slug: {directory.name}")
        for required in ("README.md", "Makefile", "tex/main.tex"):
            if not (directory / required).is_file():
                raise SystemExit(f"{directory.name}: missing {required}")
        found.append(directory.name)
    if not found:
        raise SystemExit("No articles found under articles/")
    return found


if __name__ == "__main__":
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--list", action="store_true", help="Print space-separated slugs for Make")
    args = parser.parse_args()
    articles = discover()
    print(" ".join(articles) if args.list else json.dumps(articles, separators=(",", ":")))
