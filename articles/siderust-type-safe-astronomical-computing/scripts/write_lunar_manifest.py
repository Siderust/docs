#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Identify the lunar application sources, parameters and regenerated evidence."""
import argparse,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser(__doc__);p.add_argument('--article',type=Path,required=True);a=p.parse_args();r=a.article.resolve();e=r/'experiments/lunar'
sources=['examples/Cargo.toml','examples/Cargo.lock','examples/src/lunar_application.rs','examples/src/bin/earth_from_moon.rs','examples/src/bin/lunar_geometry.rs','scripts/validate_lunar_application.py','scripts/generate_lunar_macros.py','scripts/fetch_application_kernels.py','scripts/write_lunar_manifest.py','experiments/lunar/inputs.json','experiments/reproduce.sh','experiments/requirements.txt']
files=[r/name for name in sources]+sorted((e/'recorded').glob('*'))
entries=[dict(path=p.relative_to(r).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files if p.is_file()]
(e/'manifest.json').write_text(json.dumps(dict(experiment='Earth from lunar site, 2017-10-01 17:14:00 TT',siderust_version='0.18.1',files=entries),indent=2)+'\n')
lines=[f'{v["sha256"]}  {v["path"]}\n' for v in entries];lines.append(f'{hashlib.sha256((e/"manifest.json").read_bytes()).hexdigest()}  experiments/lunar/manifest.json\n');(e/'SHA256SUMS').write_text(''.join(lines))
