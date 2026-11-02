#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Read-only integrity verification, independent of scientific Python packages."""
import hashlib
import json
from pathlib import Path

ARTICLE = Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    manifest = ARTICLE / 'experiments/results/SHA256SUMS'
    entries = []
    for line in manifest.read_text().splitlines():
        expected, name = line.split('  ', 1)
        path = ARTICLE / name
        if not path.resolve().is_relative_to(ARTICLE) or not path.is_file():
            raise RuntimeError(f'Missing or invalid publication file: {name}')
        if digest(path) != expected:
            raise RuntimeError(f'Publication checksum mismatch: {name}')
        entries.append(name)
    # Source identities also link imported evidence to the original package.
    provenance = json.loads((ARTICLE/'experiments/results/SOURCE-MANIFEST.json').read_text())
    for entry in provenance['files']:
        if digest(ARTICLE/entry['path']) != entry['sha256']:
            raise RuntimeError(f'Original evidence/source changed: {entry["path"]}')
    # These manifests include the fixed observations, models, epochs and kernels.
    for group in ('terrestrial', 'lunar'):
        base = ARTICLE/f'experiments/{group}'
        for line in (base/'SHA256SUMS').read_text().splitlines():
            expected, name = line.split('  ', 1)
            if digest(ARTICLE/name) != expected:
                raise RuntimeError(f'{group} checksum mismatch: {name}')
    print(f'Integrity passed: {len(entries)} publication files and original provenance.')
    return len(entries)


if __name__ == '__main__':
    verify()
