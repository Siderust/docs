#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Acquire only the checksum-pinned NAIF inputs for the application replay."""
import argparse,hashlib,json,urllib.request
from pathlib import Path
p=argparse.ArgumentParser(__doc__);p.add_argument('--inputs',type=Path,required=True);p.add_argument('--destination',type=Path,required=True);a=p.parse_args();a.destination.mkdir(parents=True,exist_ok=True)
for name,metadata in json.loads(a.inputs.read_text())['kernel_inputs'].items():
    path=a.destination/name
    if not path.exists():
        partial=path.with_suffix(path.suffix+'.part')
        urllib.request.urlretrieve(metadata['url'],partial)
        if hashlib.sha256(partial.read_bytes()).hexdigest()!=metadata['sha256']:
            raise RuntimeError(f'Downloaded kernel checksum mismatch: {name}')
        partial.replace(path)
    if hashlib.sha256(path.read_bytes()).hexdigest()!=metadata['sha256']:raise RuntimeError(f'Kernel checksum mismatch: {name}')
print('All three NAIF input hashes verified.')
