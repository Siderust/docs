#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Regenerate every publication result table/macro/figure, without seeding TeX."""
import json
import math
import re
import subprocess
import sys
from pathlib import Path

ARTICLE = Path(__file__).resolve().parents[2]


def ceiling(value):
    exponent = math.floor(math.log10(value))
    digit = math.ceil(value/10**exponent)
    if digit == 10:
        digit, exponent = 1, exponent+1
    return str(digit)+r'\times10^{'+str(exponent)+'}'


def generate(data, output):
    tables = output/'tex/tables'
    tables.mkdir(parents=True, exist_ok=True)
    summary = json.loads((data/'extended-summary.json').read_text())
    # The four empirical display ceilings and the altitude acceptance bound are
    # derived from evidence, not copied from the existing generated manuscript.
    constants = {
        'RotationBound': ceiling(max(summary[k]['max'] for k in ('ERA', 'GMST'))),
        'BpnBound': ceiling(summary['BPN']['max']),
        'LunarMatrixBound': ceiling(summary['lunar_matrix']['max']),
        'SurfaceAngleBound': ceiling(max(summary[k]['max'] for k in ('lunar_direction', 'lunar_finite_angle'))),
        'AltitudeBound': ceiling(summary['altitude']['bound']),
    }
    order = json.loads((Path(__file__).parent/'manifests/publication-layout.json').read_text())['macro_order']
    macros = tables/'release-values.tex'
    macros.write_text(''.join('\\newcommand{\\'+name+'}{'+constants.get(name, '')+'}\n' for name in order))
    commands = [
        ('generate_results_tables.py', '--article', output, '--data', data),
        ('generate_antares_macros.py', '--article', output, '--summary', data/'viewing-summary.json'),
        ('generate_lunar_macros.py', '--article', output, '--summary', data/'lunar-application-summary.json'),
        ('generate_figures.py', '--article', output, '--data', data/'viewing.csv'),
        ('verify_antares_figure.py', '--figure', output/'tex/figures/observing-window.tex', '--data', data/'viewing.csv'),
    ]
    for script, *args in commands:
        subprocess.run([sys.executable, str(ARTICLE/'scripts'/script), *map(str, args)], check=True)
    if re.search(r'\\newcommand\{\\\w+\}\{\}', macros.read_text()):
        raise RuntimeError('Unpopulated result macro')
    generated = [output / name for name in (ARTICLE/'generated-tex.txt').read_text().splitlines()]
    for path in generated:
        name = path.relative_to(output)
        if path.read_bytes() != (ARTICLE/name).read_bytes():
            raise RuntimeError(f'Publication output differs: {name}')
    return [p.relative_to(output).as_posix() for p in generated]
