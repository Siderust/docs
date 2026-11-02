#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Render Chapter 8 tables/macros from preserved evidence, without new experiments."""
import argparse
import json
from pathlib import Path
from table_format import scientific, statistics_row, unit


def generate(article, data):
    article, data = Path(article), Path(data)
    out = article/'tex/tables'
    out.mkdir(parents=True, exist_ok=True)
    d = json.loads((data/'extended-summary.json').read_text())
    ep = json.loads((data/'summary.json').read_text())
    controls = json.loads((data/'controls-summary.json').read_text())
    result_files = []

    def write(name, lines):
        (out/name).write_text('\n'.join(lines)+'\n')
        result_files.append(name)

    rows = [('Earth rotation angle','rad','ERA'),('GMST (IAU 2006)','rad','GMST'),
            ('Mean obliquity','rad','obliquity'),('BPN matrix element','1','BPN'),
            ('UTC to TAI$^{*}$','s','UTC_TAI_fullJD'),('UTC to TT$^{*}$','s','UTC_TT_fullJD'),
            ('Antares azimuth','deg','azimuth'),('Antares altitude','deg','altitude')]
    lines = [r'\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}llrrrrr@{}}',r'\toprule',
             r'Observable & Unit & $n$ & Median & p95 & p99 & Maximum \\',r'\midrule']
    for name,u,k in rows:
        lines.append(statistics_row(name,u,d[k]['n'],d[k]))
    for name,u,k in [('Earth heliocentric','au','Earth SPK'),('Moon geocentric','km','Moon SPK')]:
        lines.append(statistics_row(name,u,1000,ep[k]))
    write('release-validation.tex',lines+[r'\bottomrule',r'\end{tabular*}'])

    lines = [r'\begin{tabular}{@{}llrrr@{}}',r'\toprule',
             r'Conversion & Unit & $n$ & Maximum & Bound \\',r'\midrule']
    for name,k in [('UTC to TAI','UTC_TAI_split'),('UTC to TT','UTC_TT_split')]:
        v=d[k];lines.append(f'{name} & {unit("s")} & {v["n"]} & {scientific(v["max"])} & {scientific(v["bound"],0)}'+r' \\')
    write('release-time.tex',lines+[r'\bottomrule',r'\end{tabular}'])

    lines = [r'\begin{tabularx}{\columnwidth}{@{}Yrrr@{}}',r'\toprule',
             r'Model / target (unit) & Median & p95 & Maximum \\',r'\midrule']
    for name,u,k in [('VSOP87A / Earth heliocentric','au','Earth model'),('ELP2000-82B / Moon geocentric','km','Moon model')]:
        lines.append(f'{name} ({unit(u)}) & '+' & '.join(scientific(ep[k][v]) for v in ['median','p95','max'])+r' \\')
    write('release-models.tex',lines+[r'\bottomrule',r'\end{tabularx}'])

    lines = [r'\begin{tabularx}{\columnwidth}{@{}Ylrrr@{}}',r'\toprule',
             r'Observable & Unit & $n$ & Maximum & Bound \\',r'\midrule']
    for name,u,k in [('Lunar rotation matrix','1','lunar_matrix'),('Distant lunar direction angle','deg','lunar_direction'),
                     ('Finite lunar target angle','deg','lunar_finite_angle'),('Finite lunar target range','m','lunar_range'),
                     ('Finite lunar Cartesian components','m','lunar_components'),('Mars surface position','m','mars_position'),
                     ('Mars local tangent basis','1','mars_basis')]:
        v=d[k];lines.append(f'{name} & {unit(u)} & {v["n"]} & {scientific(v["max"])} & {scientific(v["bound"],0)}'+r' \\')
    write('release-surface.tex',lines+[r'\bottomrule',r'\end{tabularx}'])

    macros = {'UtcTaiSplitMax':scientific(d['UTC_TAI_split']['max'])[1:-1],
              'UtcTtSplitMax':scientific(d['UTC_TT_split']['max'])[1:-1],
              'EarthSpkMax':scientific(ep['Earth SPK']['max'])[1:-1],
              'MoonSpkMax':scientific(ep['Moon SPK']['max'])[1:-1],
              'EarthAnalyticalMax':scientific(ep['Earth model']['max'])[1:-1],
              'MoonAnalyticalMax':scientific(ep['Moon model']['max'])[1:-1],
              'BoundaryLunarCount':str(d['boundary_lunar_angles']['n']),
              'BoundaryMarsCount':str(d['boundary_mars_position']['n']),
              'BoundaryVerticalCount':str(d['boundary_vertical_cases']),
              'BoundaryTotalCount':str(d['boundary_lunar_angles']['n']+d['boundary_mars_position']['n']),
              'BoundaryLunarAngleMax':scientific(d['boundary_lunar_angles']['max'])[1:-1],
              'BoundaryMarsPositionMax':scientific(d['boundary_mars_position']['max'])[1:-1],
              'BoundaryMarsBasisMax':scientific(d['boundary_mars_basis']['max'])[1:-1],
              'StaticControlCount':str(len(controls))}
    assert 0 < d['boundary_vertical_cases'] < d['boundary_lunar_angles']['n']
    assert len(controls)==5 and all(v['expected_failure'] for v in controls.values())
    write('results-values.tex',['% Generated from unchanged experimental evidence; Chapter 8 values.',
        *['\\newcommand{\\'+key+'}{'+value+'}' for key,value in macros.items()]])
    print('Generated '+', '.join(result_files))


if __name__=='__main__':
    p=argparse.ArgumentParser(__doc__);p.add_argument('--article',type=Path,required=True);p.add_argument('--data',type=Path,required=True);a=p.parse_args()
    generate(a.article,a.data)
