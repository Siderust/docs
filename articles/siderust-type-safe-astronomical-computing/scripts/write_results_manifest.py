#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Publication maintenance only: refresh integrity after reviewed source changes.

Never run this as part of reproduction: verification must detect changed evidence.
The original import hashes in SOURCE-MANIFEST.json are never rewritten here.
"""
import argparse
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(__doc__)
parser.add_argument('--article', type=Path, required=True)
article = parser.parse_args().article.resolve()
base = article/'experiments/results'
excluded = {base/'SHA256SUMS', base/'manifest.json'}
files = set()
for prefix in ('examples', 'scripts', 'experiments'):
    for path in (article/prefix).rglob('*'):
        if not path.is_file() or path in excluded:
            continue
        parts = path.relative_to(article).parts
        if any(p in ('runs', 'target', '__pycache__', '.venv', 'pyenv') for p in parts) or path.suffix == '.pyc':
            continue
        files.add(path)
for prefix in ('tex/tables', 'tex/figures'):
    files.update((article/prefix).glob('*.tex'))
files.add(article/'README.md')
files.add(article/'rust-toolchain.toml')
files.add(article/'generated-tex.txt')
entries = [dict(path=p.relative_to(article).as_posix(), bytes=p.stat().st_size,
                sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(files)]
manifest = dict(path_base='article', policy='Original evidence is immutable; fresh runs are excluded.',
                software=dict(rust='1.93.1', siderust='0.18.1', tempoch='0.11.2',
                              python='3.12.13', pyerfa='2.0.1.5', erfa='2.0.1',
                              spiceypy='6.0.0', cspice='CSPICE_N0067', numpy='2.5.4'),
                experiment_map='experiments/results/manifests/experiments.json', files=entries)
(base/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
lines = [f'{e["sha256"]}  {e["path"]}\n' for e in entries]
lines.append(f'{hashlib.sha256((base/"manifest.json").read_bytes()).hexdigest()}  experiments/results/manifest.json\n')
(base/'SHA256SUMS').write_text(''.join(lines))
print(f'Wrote integrity entries for {len(entries)+1} publication files.')
