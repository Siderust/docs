#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Independent CSPICE reduction of the specified finite-distance lunar geometry."""
import argparse
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
import erfa
import numpy as np
import spiceypy as sp


def tdb_from_tt(seconds):
    # Independently evaluated USNO Circular 179 seven-term model, also used
    # by the pinned Tempoch release. No Siderust time output is an oracle.
    jd=2451545.+seconds/86400.
    t=(jd-2451545.)/36525.
    terms=[(0.001657,628.3076,6.2401),(0.000022,575.3385,4.2970),
           (0.000014,1256.6152,6.1969),(0.000005,606.9777,4.0212),
           (0.000005,52.9691,0.4444),(0.000002,21.3299,5.5431)]
    offset=sum(a*np.sin(b*t+c) for a,b,c in terms)+0.000010*t*np.sin(628.3076*t+4.2490)
    return seconds+offset


def validate(data,kernels,inputs):
    data,kernels=Path(data),Path(kernels);config=json.loads(Path(inputs).read_text())
    for name,metadata in config['kernel_inputs'].items():
        p=kernels/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==metadata['sha256'],name
        sp.furnsh(str(p))
    label=dt.datetime.fromisoformat(config['epoch_tt']);assert label==dt.datetime(2017,10,1,17,14)
    assert config['longitude_east_deg']==20.17 and config['planetocentric_latitude_deg']==-1.10
    day0=sum(erfa.cal2jd(label.year,label.month,label.day))
    # Integer TT seconds from calendar day and clock fields, never a UTC label.
    tt_seconds=(day0-2451545.)*86400+label.hour*3600+label.minute*60+label.second
    tdb=tdb_from_tt(tt_seconds);native_et=sp.unitim(tt_seconds,'TDT','TDB')
    with (data/'lunar-application.csv').open() as f:
        actual={row[0]:np.array([float(v) for v in row[1:] if v]) for row in list(csv.reader(f))[1:]}
    assert actual['tt_seconds'][0]==tt_seconds
    assert abs(actual['tdb_seconds'][0]-tdb)<=np.spacing(tdb)
    rotation=sp.pxform('J2000','IAU_MOON',tdb)
    inertial=sp.spkpos('EARTH',tdb,'J2000','NONE','MOON')[0]
    lon,lat=np.deg2rad([config['longitude_east_deg'],config['planetocentric_latitude_deg']])
    up=np.array([np.cos(lat)*np.cos(lon),np.cos(lat)*np.sin(lon),np.sin(lat)])
    north=np.array([-np.sin(lat)*np.cos(lon),-np.sin(lat)*np.sin(lon),np.cos(lat)])
    east=np.array([-np.sin(lon),np.cos(lon),0.])
    observer=config['reference_radius_km']*up
    fixed=rotation@inertial;relative=fixed-observer
    horizontal=np.array([north@relative,east@relative,up@relative])
    def angles(v):return np.array([np.rad2deg(np.arctan2(v[2],np.hypot(v[0],v[1]))),np.rad2deg(np.arctan2(v[1],v[0]))%360,np.linalg.norm(v)])
    values=angles(horizontal);center=angles(np.array([north@fixed,east@fixed,up@fixed]))
    residuals={}
    reference={'inertial_km':inertial,'fixed_km':fixed,'observer_km':observer,'relative_km':relative,'horizontal_km':horizontal}
    for name,v in reference.items():
        residuals[name]=float(max(abs(actual[name]-v)));assert residuals[name]<1e-4,(name,residuals[name])
    matrix_error=float(np.max(abs(np.vstack([actual[f'rotation_{i}'] for i in range(3)])-rotation)))
    assert matrix_error<1e-10
    altitude_error=abs(actual['altitude_deg'][0]-values[0]);azimuth_error=abs((actual['azimuth_deg'][0]-values[1]+180)%360-180);range_error=abs(actual['range_km'][0]-values[2]);center_error=abs(actual['center_altitude_deg'][0]-center[0])
    assert max(altitude_error,azimuth_error,center_error)<3e-9
    assert range_error<2e-8
    assert abs(actual['parallax_deg'][0]-(center[0]-values[0]))<3e-9
    assert actual['tt_jd'][0]==day0+(label.hour*3600+label.minute*60+label.second)/86400
    # Independently verify coverage of both kernel body segments.
    for body in [301,399]:
        coverage=sp.spkcov(str(kernels/'de440s.bsp'),body)
        assert any(sp.wnfetd(coverage,i)[0]<=tdb<=sp.wnfetd(coverage,i)[1] for i in range(sp.wncard(coverage)))
    raw_et_inertial=sp.spkpos('EARTH',native_et,'J2000','NONE','MOON')[0]
    raw_et_fixed=sp.pxform('J2000','IAU_MOON',native_et)@raw_et_inertial
    raw_et_values=angles(np.array([north@(raw_et_fixed-observer),east@(raw_et_fixed-observer),up@(raw_et_fixed-observer)]))
    reference.update(tt_seconds=[tt_seconds],tdb_seconds=[tdb],altitude_deg=[values[0]],azimuth_deg=[values[1]],range_km=[values[2]],center_altitude_deg=[center[0]],parallax_deg=[center[0]-values[0]])
    with (data/'lunar-application-reference.csv').open('w') as f:
        writer=csv.writer(f);writer.writerow(['quantity','x','y','z'])
        for name,v in reference.items():writer.writerow([name,*[float(x) for x in v]])
        for i,row in enumerate(rotation):writer.writerow([f'rotation_{i}',*[float(x) for x in row]])
    summary=dict(epoch_tt=config['epoch_tt'],longitude_east_deg=config['longitude_east_deg'],planetocentric_latitude_deg=config['planetocentric_latitude_deg'],
        tt_seconds=tt_seconds,tdb_seconds=tdb,altitude_deg=float(actual['altitude_deg'][0]),azimuth_deg=float(actual['azimuth_deg'][0]),range_km=float(actual['range_km'][0]),
        center_altitude_deg=float(actual['center_altitude_deg'][0]),parallax_deg=float(actual['parallax_deg'][0]),
        reference=[float(x) for x in values],rust=[float(actual[k][0]) for k in ['altitude_deg','azimuth_deg','range_km']],
        absolute_residuals=[float(altitude_error),float(azimuth_error),float(range_error)],center_altitude=float(center[0]),parallax=float(center[0]-values[0]),
        vector_max_residuals_km=residuals,vector_component_bound_km=1e-4,matrix_max_residual=matrix_error,center_altitude_residual_deg=float(center_error),
        angle_bound_deg=3e-9,range_bound_km=2e-8,
        native_unitim_diagnostic=dict(et_seconds=float(native_et),time_difference_seconds=float(tdb-native_et),
            altitude_residual_deg=float(abs(actual['altitude_deg'][0]-raw_et_values[0])),azimuth_residual_deg=float(abs((actual['azimuth_deg'][0]-raw_et_values[1]+180)%360-180)),range_residual_km=float(abs(actual['range_km'][0]-raw_et_values[2]))),
        kernel_coverage_verified=True,kernels_sha256={n:m['sha256'] for n,m in config['kernel_inputs'].items()},
        versions=dict(pyerfa=erfa.__version__,erfa=erfa.version.erfa_version,spiceypy=sp.__version__,cspice=sp.tkvrsn('TOOLKIT'),numpy=np.__version__))
    (data/'lunar-application-summary.json').write_text(json.dumps(summary,indent=2)+'\n');sp.kclear();return summary

if __name__=='__main__':
    p=argparse.ArgumentParser(__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--kernels',type=Path,required=True);p.add_argument('--inputs',type=Path,required=True);a=p.parse_args()
    print(json.dumps(validate(a.data,a.kernels,a.inputs),indent=2))
