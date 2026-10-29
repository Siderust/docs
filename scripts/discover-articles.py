#!/usr/bin/env python3
"""Print the JSON matrix of independently buildable LaTeX articles."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / "articles"


def discover():
    found = []
    for directory in sorted(ARTICLES.iterdir()):
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
    print(json.dumps(discover(), separators=(",", ":")))
