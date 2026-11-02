#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Retrieve the original public regression sources, without modifying them."""
import hashlib
import json
import shutil
import tarfile
import urllib.request
from pathlib import Path, PurePosixPath


def fetch(destination):
    manifest = Path(__file__).parent/'manifests/upstream.json'
    sources = json.loads(manifest.read_text())['sources']
    destination.mkdir(parents=True, exist_ok=True)
    for source in sources:
        archive = destination/(source['name']+'.tar.gz')
        print(f'Downloading {source["name"]} at {source["revision"]}', flush=True)
        urllib.request.urlretrieve(source['url'], archive)
        if hashlib.sha256(archive.read_bytes()).hexdigest() != source['archive_sha256']:
            raise RuntimeError(f'Upstream archive checksum mismatch: {source["name"]}')
        target = destination/source['name']
        target.mkdir()
        expected = {f['path']: f['sha256'] for f in source['files']}
        actual = set()
        with tarfile.open(archive) as bundle:
            for member in bundle:
                parts = PurePosixPath(member.name).parts[1:]
                if not parts or member.isdir():
                    continue
                name = PurePosixPath(*parts).as_posix()
                if '..' in parts or member.name.startswith('/') or not member.isfile() or name not in expected:
                    raise RuntimeError(f'Unexpected upstream archive entry: {member.name}')
                path = target/name
                path.parent.mkdir(parents=True, exist_ok=True)
                with bundle.extractfile(member) as src, path.open('wb') as dst:
                    shutil.copyfileobj(src, dst)
                if hashlib.sha256(path.read_bytes()).hexdigest() != expected[name]:
                    raise RuntimeError(f'Upstream file checksum mismatch: {name}')
                actual.add(name)
        if actual != set(expected):
            raise RuntimeError(f'Incomplete upstream source: {source["name"]}')
    return {s['name']: destination/s['name'] for s in sources}
