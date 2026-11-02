#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Recompile all five original negative fixtures; retain every diagnostic."""
import json
import os
import subprocess
from pathlib import Path


def check(output):
    root = Path(__file__).parent
    results = {}
    for name in ('dimension', 'frame', 'center', 'scale', 'observer_body'):
        command = ['cargo', '+1.93.1', 'check', '--locked', '--manifest-path',
                   str(root/'controls/Cargo.toml'), '--bin', name]
        process = subprocess.run(command, capture_output=True, text=True, env=os.environ)
        (output/f'control-{name}.log').write_text(process.stdout+process.stderr)
        code = 'E0308' if name in ('dimension', 'scale', 'observer_body') else 'E0277'
        if process.returncode == 0 or code not in process.stderr:
            raise RuntimeError(f'{name}: expected compiler rejection {code}; see its log')
        results[name] = {'expected_failure': True, 'diagnostic': code}
    (output/'controls-summary.json').write_text(json.dumps(results, indent=2)+'\n')
    return results
