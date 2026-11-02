#!/usr/bin/env python3
"""Format hand-edited TeX and check hygiene without touching generated sources."""
import argparse
from pathlib import Path
import re
import subprocess
import tempfile


def sources(article):
    generated = set()
    inventory = article / 'generated-tex.txt'
    if inventory.exists():
        generated = {article / line for line in inventory.read_text().splitlines() if line}
        if any(not p.is_file() or not p.resolve().is_relative_to(article) for p in generated):
            raise SystemExit('Invalid generated-tex.txt entry')
    return sorted(p for p in (article / 'tex').rglob('*.tex')
                  if 'build' not in p.relative_to(article).parts and p not in generated)


def hygiene(path, data):
    text = data.decode('utf-8')
    errors = []
    if b'\r' in data:
        errors.append('use LF line endings')
    if not data.endswith(b'\n'):
        errors.append('missing final newline')
    if any(line.rstrip(' \t') != line for line in text.splitlines()):
        errors.append('trailing whitespace')
    if re.search(r'^(?:<{7}|={7}|>{7})(?:\s|$)', text, re.M):
        errors.append('merge conflict marker')
    return errors


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('mode', choices=('fmt', 'fmt-check', 'hygiene'))
    parser.add_argument('article', type=Path)
    args = parser.parse_args()
    article = args.article.resolve()
    failed = False
    paths = sources(article)
    if not paths:
        parser.error('No hand-edited TeX sources found')
    for path in paths:
        original = path.read_bytes()
        if args.mode != 'hygiene':
            with tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary) / 'formatted.tex'
                subprocess.run(['latexindent', '-s', '-m', '-l='+str(article / '.latexindent.yaml'),
                                '-c='+temporary, '-o='+str(output), str(path)], check=True,
                               stdout=subprocess.DEVNULL)
                formatted = output.read_text()
            formatted = '\n'.join(line.rstrip() for line in formatted.splitlines()).rstrip()+'\n'
            if args.mode == 'fmt':
                path.write_text(formatted)
            elif original != formatted.encode():
                print(f'{path.relative_to(article)}: run make fmt')
                failed = True
        # Check generated files as well below, without reformatting them.
    for path in sorted((article / 'tex').rglob('*.tex')):
        if 'build' in path.relative_to(article).parts:
            continue
        for error in hygiene(path, path.read_bytes()):
            print(f'{path.relative_to(article)}: {error}')
            failed = True
    raise SystemExit(int(failed))


if __name__ == '__main__':
    main()
