#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Generate the Antares observing-window figure from the recorded Rust grid."""
import argparse
import csv
import math
from pathlib import Path

p = argparse.ArgumentParser(__doc__)
p.add_argument('--article', type=Path, required=True)
p.add_argument('--data', type=Path, required=True)
a = p.parse_args()
rows = [[float(v) for v in row] for row in csv.reader(a.data.open())]
assert len(rows) == 289 and [int(v[0]) for v in rows] == list(range(289))
threshold = 15.0
points = [(row[0]/12, row[2]) for row in rows]
selected = [(x, y) for x, y in points if y > threshold]
with (a.data.parent/'viewing-events.csv').open() as f:
    event_rows = list(csv.DictReader(f))
roots = [float(row['start_ut1_seconds'])/3600 for row in event_rows if row['kind'] in ['Rising','Setting']]
brackets = [(i, i+1) for i in range(288)
            if (points[i][1] > threshold) != (points[i+1][1] > threshold)]
assert selected and len(brackets) == len(roots)


def coords(values):
    return '\n'.join(f'({x:.9f},{y:.10f})' for x, y in values)


def clock(index):
    minutes = index*5
    return f'{minutes//60:02d}:{minutes%60:02d}'


lines = [f'% Generated from viewing.csv: {len(rows)} samples, {len(selected)} selected, {len(brackets)} brackets.',
         r'\begin{tikzpicture}[x=0.64cm,y=0.035cm,font=\scriptsize]',
         r'\draw[->] (0,-80) -- (24.7,-80);',
         r'\draw[->] (0,-80) -- (0,29);']
for h in range(0, 25, 4):
    lines.append(fr'\draw ({h},-80) -- ({h},-82) node[below] {{{h:02d}:00}};')
for y in [-75, -50, -25, 0, 15, 25]:
    lines.append(fr'\draw (0,{y}) -- (-0.15,{y}) node[left] {{{y}}};')
for i, j in brackets:
    assert (rows[i][2]-threshold)*(rows[j][2]-threshold) < 0
    lines.append(fr'\fill[orange!35] ({i/12:.9f},-80) rectangle ({j/12:.9f},25);')
lines += [r'\draw[dashed] (0,15) -- (24,15);',
          r'\draw[black!55,thin] plot coordinates {'+coords(points)+'};']
for x, y in selected:
    lines.append(fr'\filldraw[fill=white,draw=blue!80!black,line width=0.4pt] ({x:.9f},{y:.10f}) circle[radius=0.65pt];')
lines += [r'\node[rotate=90] at (-1.2,-25) {Geometric altitude (deg)};',
          r'\node at (12,-95) {1896 July 14 UT1 (24:00 = July 15)};',
          r'\node[anchor=south,align=center] at (12,40) {Antares: fixed ICRS catalog direction; geometric altitude selection};',
          r'\node[anchor=south west] at (0,25) {Open: $h>15^\circ$; bands: five-minute brackets; dotted: refined crossings};']
# One inset per actual crossing, rather than a prescribed morning/evening pair.
for k, (i, j) in enumerate(brackets):
    lo, hi = max(0, i-2), min(288, j+2)
    width = (hi-lo)/12
    subset = points[lo:hi+1]
    bottom = math.floor(min(y for x, y in subset))
    top = math.ceil(max(y for x, y in subset))
    origin = 3 + 12*(k % 2)
    vertical = -175 - 100*(k//2)
    title = 'Rising' if rows[j][2] > rows[i][2] else 'Falling'
    lines += [fr'\begin{{scope}}[shift={{({origin},{vertical})}},x=9cm,y=0.45cm]',
              fr'\fill[orange!35] ({(i-lo)/12:.9f},0) rectangle ({(j-lo)/12:.9f},{top-bottom});',
              fr'\draw[->] (0,0) -- ({width+0.025:.9f},0);',
              fr'\draw[->] (0,0) -- (0,{top-bottom+0.5});',
              fr'\draw[dashed] (0,{threshold-bottom:g}) -- ({width:.9f},{threshold-bottom:g});']
    for y in range(bottom, top+1):
        lines.append(fr'\draw (0,{y-bottom}) -- (-0.008,{y-bottom}) node[left] {{{y}}};')
    lines.append(fr'\draw[densely dotted,thick] ({roots[k]-lo/12:.9f},0) -- ({roots[k]-lo/12:.9f},{top-bottom});')
    for n in [lo, i, j, hi]:
        lines.append(fr'\draw ({(n-lo)/12:.9f},0) -- ({(n-lo)/12:.9f},-0.12) node[below] {{{clock(n)}}};')
    lines.append(r'\draw[black!55,thin] plot coordinates {'+
                 coords([((n-lo)/12, rows[n][2]-bottom) for n in range(lo, hi+1)])+'};')
    for n in range(lo, hi+1):
        style = 'fill=white,draw=blue!80!black' if rows[n][2] > threshold else 'fill=black!55,draw=black!55'
        lines.append(fr'\filldraw[{style},line width=0.5pt] ({(n-lo)/12:.9f},{rows[n][2]-bottom:.10f}) circle[radius=1.2pt];')
    lines += [fr'\node at ({width/2:.9f},{top-bottom+0.9}) {{{title}: {clock(i)}--{clock(j)} UT1}};', r'\end{scope}']
lines.append(r'\end{tikzpicture}')
out = a.article/'tex/figures'
out.mkdir(parents=True, exist_ok=True)
(out/'observing-window.tex').write_text('\n'.join(lines)+'\n')
print(f'Generated observing-window.tex: {len(rows)} samples, {len(selected)} selected, {len(brackets)} brackets.')
