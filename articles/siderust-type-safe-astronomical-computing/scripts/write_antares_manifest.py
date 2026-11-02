#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Refresh the terrestrial evidence and source checksum manifest after review."""
import argparse
import hashlib
import json
from pathlib import Path

p = argparse.ArgumentParser(__doc__)
p.add_argument('--article', type=Path, required=True)
a = p.parse_args()
r = a.article.resolve()
e = r/'experiments/terrestrial'
sources = ['examples/Cargo.toml', 'examples/Cargo.lock', 'examples/src/antares.rs',
           'examples/src/bin/viewing.rs', 'examples/src/bin/observe.rs',
           'examples/src/bin/antares_diagnostics.rs', 'examples/src/bin/viewing_events.rs',
           'examples/src/bin/historical_feasibility.rs', 'scripts/validate_antares.py',
           'scripts/table_format.py', 'scripts/generate_figures.py', 'scripts/generate_antares_macros.py',
           'scripts/verify_antares_figure.py', 'scripts/write_antares_manifest.py',
           'experiments/terrestrial/catalog.json', 'experiments/terrestrial/requirements.txt',
           'experiments/terrestrial/reproduce.sh']
files = [r/p for p in sources]+sorted((e/'recorded').glob('*'))
entries = [dict(path=p.relative_to(r).as_posix(), bytes=p.stat().st_size,
                sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files if p.is_file()]
manifest = dict(experiment='Antares fixed-catalog geometric altitude, 1896-07-14 UT1',
                siderust_version='0.18.1', reference_python='3.12.13',
                data_policy='Regenerated terrestrial subset; unrelated publication evidence retained. Replays write new runs/<id> directories.',
                files=entries)
(e/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
lines = [f'{p["sha256"]}  {p["path"]}\n' for p in entries]
lines.append(f'{hashlib.sha256((e/"manifest.json").read_bytes()).hexdigest()}  experiments/terrestrial/manifest.json\n')
(e/'SHA256SUMS').write_text(''.join(lines))
