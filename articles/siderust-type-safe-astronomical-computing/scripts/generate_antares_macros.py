#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Update only terrestrial result macros from the validated numerical summary."""
import argparse
import json
import re
from pathlib import Path
from table_format import statistics_row

p = argparse.ArgumentParser(__doc__)
p.add_argument('--article', type=Path, required=True)
p.add_argument('--summary', type=Path, required=True)
a = p.parse_args()
s = json.loads(a.summary.read_text())
assert s['count'] == 289 and s['selected'] > 0
values = dict(ViewingSampleCount=str(s['count']), ViewingSelectedCount=str(s['selected']),
              ViewingSpans=' and '.join('--'.join(span) for span in s['spans_ut1']),
              ViewingBrackets=' and '.join('--'.join(pair) for pair in s['crossing_brackets_ut1']),
              ViewingMaximumAltitude=f"{s['maximum_sampled_altitude_deg']:.6f}",
              ViewingMaximumTime=s['maximum_sample_ut1'],
              ViewingAltitudeResidual=f"{s['altitude']['max']:.3e}",
              ViewingAzimuthResidual=f"{s['azimuth']['max']:.3e}")
def scientific(value):
    mantissa, exponent = f'{value:.3e}'.split('e')
    return mantissa+r'\times10^{'+str(int(exponent))+'}'

values['ViewingAltitudeResidual'] = scientific(s['altitude']['max'])
values['ViewingAzimuthResidual'] = scientific(s['azimuth']['max'])
values['ViewingGstAltitudeResidual'] = scientific(s['gst06a_diagnostic']['altitude_max_deg'])
values['ViewingGstAzimuthResidual'] = scientific(s['gst06a_diagnostic']['azimuth_max_deg'])
values['ViewingRefinedSpans'] = '--'.join(s['planning']['interval_ut1'])
values['ViewingEventTolerance'] = f"{s['planning']['time_tolerance_seconds']:g}"
values['ViewingEventResidual'] = scientific(s['planning']['max_crossing_residual_seconds'])
values['ViewingCulminationAltitude'] = f"{s['planning']['maximum_altitude_deg']:.6f}"
values['ViewingCulminationTime'] = s['planning']['maximum_time_ut1']
values['ViewingDeltaTStart'] = f"{s['delta_t_start_seconds']:.6f}"
values['ViewingDeltaTEnd'] = f"{s['delta_t_end_seconds']:.6f}"
values['ViewingSiderealDifference'] = scientific(s['sidereal_diagnostics']['erfa_formulation_difference_max_rad'])
p = a.article/'tex/tables/release-values.tex'
text = p.read_text()
for name, value in values.items():
    pattern = r'\\newcommand\{\\'+name+r'\}\{[^\n]*\}'
    replacement = '\\newcommand{\\'+name+'}{'+value+'}'
    if re.search(pattern, text):
        text = re.sub(pattern, lambda _: replacement, text)
    else:
        text += replacement+'\n'
p.write_text(text)

# Replace only the two terrestrial rows; all other results stay byte-identical.
p = a.article/'tex/tables/release-validation.tex'
lines = p.read_text().splitlines()
for i, line in enumerate(lines):
    for observable in ['altitude', 'azimuth']:
        if line.startswith(('Case: '+observable+' &', 'Antares '+observable+' &')):
            v = s[observable]
            lines[i] = statistics_row('Antares '+observable, 'deg', v['n'], v)
p.write_text('\n'.join(lines)+'\n')
