#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check every plotted value, selected marker and inset against the Rust grid."""
import argparse
import csv
import math
import re
from pathlib import Path

p = argparse.ArgumentParser(__doc__)
p.add_argument('--figure', type=Path, required=True)
p.add_argument('--data', type=Path, required=True)
a = p.parse_args()
s = a.figure.read_text()
rows = [[float(v) for v in row] for row in csv.reader(a.data.open())]
assert len(rows) == 289 and [r[0] for r in rows] == list(range(289))
threshold = 15
points = [(r[0]/12, r[2]) for r in rows]
brackets = [(i, i+1) for i in range(288)
            if (rows[i][2] > threshold) != (rows[i+1][2] > threshold)]


def coordinates(text):
    curve = text.split('plot coordinates {', 1)[1].split('};', 1)[0]
    return [tuple(map(float, p)) for p in re.findall(r'\(([-\d.]+),([-\d.]+)\)', curve)]


def check_pairs(actual, expected, y_tolerance=5.1e-11):
    assert len(actual) == len(expected), (len(actual), len(expected))
    for (x, y), (u, v) in zip(actual, expected):
        assert abs(x-u) <= 5.1e-10 and abs(y-v) <= y_tolerance


panels = s.split(r'\begin{scope}')
main = panels[0]
check_pairs(coordinates(main), points)
markers = [tuple(map(float, p)) for p in re.findall(
    r'\\filldraw\[fill=white[^\]]+\] \(([-\d.]+),([-\d.]+)\)', main)]
check_pairs(markers, [(x,y) for x,y in points if y > threshold])
bands = [tuple(map(float, p)) for p in re.findall(
    r'\\fill\[orange!35\] \(([-\d.]+),-80\) rectangle \(([-\d.]+),25\)', main)]
check_pairs(bands, [(i/12, j/12) for i,j in brackets], y_tolerance=5.1e-10)
assert len(panels)-1 == len(brackets)
with (a.data.parent/'viewing-events.csv').open() as f:
    event_rows=list(csv.DictReader(f))
roots=[float(row['start_ut1_seconds'])/3600 for row in event_rows if row['kind'] in ['Rising','Setting']]
assert len(roots)==len(brackets)
for panel, (i,j), root in zip(panels[1:], brackets, roots):
    lo, hi = max(0,i-2), min(288,j+2)
    bottom = math.floor(min(rows[n][2] for n in range(lo,hi+1)))
    check_pairs(coordinates(panel), [((n-lo)/12,rows[n][2]-bottom) for n in range(lo,hi+1)])
    inset_markers = [tuple(map(float, p)) for p in re.findall(
        r'\\filldraw\[[^\]]+\] \(([-\d.]+),([-\d.]+)\)', panel)]
    check_pairs(inset_markers, [((n-lo)/12, rows[n][2]-bottom) for n in range(lo,hi+1)])
    assert (rows[i][2]-threshold)*(rows[j][2]-threshold) < 0
    assert j-i == 1
    line=re.search(r'\\draw\[densely dotted,thick\] \(([-\d.]+),0\) --', panel)
    assert line is not None and abs(float(line.group(1))-(root-lo/12))<5.1e-10
assert r'\draw[dashed] (0,15) -- (24,15);' in main
assert '1896 July 14 UT1 (24:00 = July 15)' in main
assert all(-80 < y < 25 for x,y in points)
print(f'Figure verified: {len(points)} values, {len(markers)} selected markers, '
      f'{len(brackets)} five-minute bands and data-matched insets.')
