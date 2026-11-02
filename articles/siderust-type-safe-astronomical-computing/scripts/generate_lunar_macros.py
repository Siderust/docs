#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Generate lunar application results only, preserving unrelated macros."""
import argparse,json,re
from pathlib import Path
p=argparse.ArgumentParser(__doc__);p.add_argument('--article',type=Path,required=True);p.add_argument('--summary',type=Path,required=True);a=p.parse_args();s=json.loads(a.summary.read_text())
def sci(x):
    m,e=f'{x:.3e}'.split('e');return m.rstrip('0').rstrip('.')+r'\times10^{'+str(int(e))+'}'
values=dict(EarthAltitude=f"{s['altitude_deg']:.6f}",EarthAzimuth=f"{s['azimuth_deg']:.6f}",EarthRange=f"{s['range_km']:.3f}",CentreAltitude=f"{s['center_altitude_deg']:.6f}",EarthParallax=f"{s['parallax_deg']:.5f}",EarthAngleBound=sci(s['angle_bound_deg']),EarthRangeBound=sci(s['range_bound_km']),LunarAngleResidual=sci(max(s['absolute_residuals'][:2])),LunarRangeResidual=sci(s['absolute_residuals'][2]),LunarComponentResidual=sci(max(s['vector_max_residuals_km'].values())))
p=a.article/'tex/tables/release-values.tex';text=p.read_text()
for name,value in values.items():
    pattern=r'\\newcommand\{\\'+name+r'\}\{[^\n]*\}';replacement='\\newcommand{\\'+name+'}{'+value+'}'
    if re.search(pattern,text):text=re.sub(pattern,lambda _:replacement,text)
    else:text+=replacement+'\n'
p.write_text(text)
