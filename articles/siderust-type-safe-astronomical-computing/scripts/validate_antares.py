#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Independent ERFA reduction of the historical UT1 grid and refined events."""
import argparse
import csv
import datetime as dt
import json
from pathlib import Path
import erfa
import numpy as np

ALTITUDE_BOUND = 3e-11
AZIMUTH_BOUND = 1e-10


def delta_t(catalog, jd):
    m = catalog['historical_delta_t']
    i = int((jd-m['table_origin_jd_ut1'])/m['step_days'])
    values = (m['selected_values_seconds'] if i == m['selected_index'] else
              m['alternative_values_seconds'] if i == m['alternative_index'] else None)
    assert values is not None, 'reference knots do not cover this date'
    n = (jd-(m['table_origin_jd_ut1']+m['step_days']*i))/m['step_days']
    a, b = values[1]-values[0], values[2]-values[1]
    return values[0]+n*a+n*(n-1)*(b-a)/2


def reference_at(catalog, seconds, canonical_gast=False, start=None):
    label = dt.datetime.fromisoformat(start or catalog['ut1_start'])
    base = sum(erfa.cal2jd(label.year,label.month,label.day))
    ut1 = base+float(seconds)/86400
    offset = delta_t(catalog,ut1)
    tt = ut1+offset/86400
    vector = erfa.s2c(*np.deg2rad([catalog['ra_deg'],catalog['dec_deg']]))
    of_date = erfa.pnm06a(tt,0)@vector
    ra, dec = erfa.c2s(of_date)
    dp, _ = erfa.nut06a(tt,0)
    gast = (erfa.gst06a(ut1,0,tt,0) if canonical_gast else
            erfa.gmst06(ut1,0,tt,0)+erfa.ee00(tt,0,erfa.obl06(tt,0),dp))
    az, alt = erfa.hd2ae(gast+np.deg2rad(catalog['observer']['longitude_east_deg'])-ra,
                       dec,np.deg2rad(catalog['observer']['geodetic_latitude_north_deg']))
    return np.array([ut1,tt,np.rad2deg(ra)%360,np.rad2deg(dec),np.rad2deg(alt),np.rad2deg(az)%360,offset])


def reference(catalog, indices, canonical_gast=False):
    return np.array([reference_at(catalog,int(i)*300,canonical_gast) for i in indices])


def statistics(values,bound):
    assert np.all(np.isfinite(values)) and max(values)<=bound,(max(values),bound)
    return dict(n=len(values),median=float(np.median(values)),p95=float(np.percentile(values,95)),
                p99=float(np.percentile(values,99)),max=float(max(values)),bound=bound)


def clock(index):
    minutes=int(index)*5
    return f'{minutes//60:02d}:{minutes%60:02d}'


def precise_clock(seconds):
    seconds=int(round(seconds));return f'{seconds//3600:02d}:{seconds%3600//60:02d}:{seconds%60:02d}'


def bisect(catalog,lo,hi):
    f=lambda t:reference_at(catalog,t)[4]-catalog['threshold_deg']
    a=f(lo)
    assert a*f(hi)<0
    while hi-lo>0.001:
        mid=(lo+hi)/2
        if a*f(mid)>0:lo=mid
        else:hi=mid
    return (lo+hi)/2


def validate(data,catalog_path,representative=False):
    data=Path(data);catalog=json.loads(Path(catalog_path).read_text())
    actual=np.loadtxt(data/'viewing.csv',delimiter=',',ndmin=2)
    assert actual.shape == ((3,4) if representative else (289,4))
    indices=actual[:,0].astype(int)
    assert np.array_equal(indices,np.array([0,144,288]) if representative else np.arange(289))
    assert catalog['ut1_start']=='1896-07-14T00:00:00' and catalog['ut1_end']=='1896-07-15T00:00:00'
    assert catalog['observer']['longitude_east_deg']==2.15017 and catalog['observer']['geodetic_latitude_north_deg']==41.35403
    assert catalog['threshold_deg']==15 and catalog['cadence_seconds']==300
    ref=reference(catalog,indices)
    epochs=np.genfromtxt(data/'viewing-epochs.csv',delimiter=',',names=True,dtype=None,encoding='utf-8')
    start=dt.datetime.fromisoformat(catalog['ut1_start'])
    for i,row in zip(indices,epochs):assert dt.datetime.fromisoformat(row['ut1'])==start+dt.timedelta(seconds=int(i)*300)
    assert np.array_equal(epochs['index'],indices)
    assert np.array_equal(epochs['jd_tt'],actual[:,1])
    assert np.array_equal(epochs['jd_ut1'],ref[:,0])
    assert max(abs(epochs['delta_t_seconds']-ref[:,6]))<1e-12
    assert max(abs(actual[:,1]-ref[:,1]))<=np.spacing(ref[0,1])
    wrap=lambda a,b:abs((a-b+180)%360-180)
    ra_error=wrap(epochs['ra_true_deg'],ref[:,2]);dec_error=abs(epochs['dec_true_deg']-ref[:,3])
    assert max(ra_error)<3e-11 and max(dec_error)<3e-11
    alt_error=abs(actual[:,2]-ref[:,4]);az_error=wrap(actual[:,3],ref[:,5])
    altitude=statistics(alt_error,ALTITUDE_BOUND);azimuth=statistics(az_error,AZIMUTH_BOUND)
    np.savetxt(data/'viewing-reference.csv',ref[:,4:6],delimiter=',')
    np.savetxt(data/'viewing-reference-epochs.csv',np.column_stack([indices,ref]),delimiter=',',header='index,jd_ut1,jd_tt,ra_true_deg,dec_true_deg,alt_deg,az_deg,delta_t_seconds')
    np.savetxt(data/'viewing-residuals.csv',np.column_stack([indices,alt_error,az_error]),delimiter=',',header='index,altitude_abs_deg,azimuth_wrapped_abs_deg')
    np.savetxt(data/'figure-reference.csv',np.column_stack([indices/12,actual[:,2],ref[:,4]]),delimiter=',',header='hour,rust_alt,erfa_alt')
    threshold=catalog['threshold_deg'];selected=indices[actual[:,2]>threshold]
    assert np.array_equal(selected,indices[ref[:,4]>threshold])
    spans=[];brackets=[]
    if not representative:
        for group in np.split(selected,np.flatnonzero(np.diff(selected)!=1)+1):
            if len(group):spans.append([int(group[0]),int(group[-1])])
        brackets=[[i,i+1] for i in range(288) if (actual[i,2]>threshold)!=(actual[i+1,2]>threshold)]
        for file,expected in [('viewing-spans.csv',spans),('viewing-brackets.csv',brackets)]:
            with (data/file).open() as f:assert [[int(v) for v in row] for row in list(csv.reader(f))[1:]]==expected
        with (data/'viewing-selected.csv').open() as f:rows=list(csv.DictReader(f))
        assert [int(row['index']) for row in rows]==selected.tolist()
        for row in rows:
            i=int(row['index']);assert float(row['altitude_deg'])==actual[i,2]
            assert dt.datetime.fromisoformat(row['ut1'])==start+dt.timedelta(seconds=i*300)
    standard=reference(catalog,indices,True);np.savetxt(data/'viewing-gst06a-reference.csv',standard[:,4:6],delimiter=',')
    assert np.array_equal(selected,indices[standard[:,4]>threshold])
    s_alt=abs(actual[:,2]-standard[:,4]);s_az=wrap(actual[:,3],standard[:,5]);maximum=int(np.argmax(actual[:,2]))
    result=dict(target=catalog['target'],date='1896-07-14',time_scale='UT1',count=len(indices),selected=len(selected),indices=selected.tolist(),spans=spans,
                spans_ut1=[[clock(i),clock(j)] for i,j in spans],crossing_brackets=brackets,
                crossing_brackets_ut1=[[clock(i),clock(j)] for i,j in brackets],
                maximum_sampled_altitude_deg=float(actual[maximum,2]),maximum_sample_ut1=clock(indices[maximum]),
                altitude=altitude,azimuth=azimuth,max_altitude_difference_deg=altitude['max'],
                delta_t_start_seconds=float(ref[0,6]),delta_t_end_seconds=float(ref[-1,6]),
                max_tt_difference_days=float(max(abs(actual[:,1]-ref[:,1]))),
                frame_checks=dict(ra_max_deg=float(max(ra_error)),dec_max_deg=float(max(dec_error))),
                gst06a_diagnostic=dict(altitude_max_deg=float(max(s_alt)),azimuth_max_deg=float(max(s_az)),
                    original_altitude_bound_passed=bool(max(s_alt)<=ALTITUDE_BOUND),original_azimuth_bound_passed=bool(max(s_az)<=AZIMUTH_BOUND)),
                sidereal_reference='gmst06 + ee00(obl06,nut06a.dpsi)',
                versions=dict(pyerfa=erfa.__version__,erfa=erfa.version.erfa_version,numpy=np.__version__))
    if not representative:
        diag=np.genfromtxt(data/'sidereal-diagnostics.csv',delimiter=',',names=True)
        tt,ut=ref[:,1],ref[:,0];dp,_=erfa.nut06a(tt,0);gmst=erfa.gmst06(ut,0,tt,0);implemented=gmst+erfa.ee00(tt,0,erfa.obl06(tt,0),dp);canonical=erfa.gst06a(ut,0,tt,0)
        result['sidereal_diagnostics']=dict(gmst_max_rad=float(max(abs(diag['gmst']-gmst))),implemented_gast_max_rad=float(max(abs(diag['gast']-implemented))),gst06a_gast_max_rad=float(max(abs(diag['gast']-canonical))),erfa_formulation_difference_max_rad=float(max(abs(implemented-canonical))))
        assert result['sidereal_diagnostics']['gmst_max_rad']<6e-14
        with (data/'viewing-events.csv').open() as f:events=list(csv.DictReader(f))
        crossings=[row for row in events if row['kind'] in ['Rising','Setting']]
        assert len(crossings)==len(brackets)
        roots=[bisect(catalog,i*300,j*300) for i,j in brackets]
        errors=[]
        with (data/'viewing-events-reference.csv').open('w') as f:
            writer=csv.writer(f);writer.writerow(['kind','rust_ut1_seconds','erfa_ut1_seconds','absolute_seconds'])
            for row,(i,j),root in zip(crossings,brackets,roots):
                seconds=float(row['start_ut1_seconds']);assert i*300<=seconds<=j*300
                error=abs(seconds-root);assert error<=1.0,error;errors.append(error)
                writer.writerow([row['kind'],seconds,root,error])
        intervals=[row for row in events if row['kind']=='interval'];assert len(intervals)==1
        refined_start=float(intervals[0]['start_ut1_seconds']);refined_end=float(intervals[0]['end_ut1_seconds'])
        assert abs(refined_start-roots[0])<=1 and abs(refined_end-roots[1])<=1
        for row in events:
            if row['kind'] in ['Min','Max']:
                expected_alt=reference_at(catalog,float(row['start_ut1_seconds']))[4]
                assert abs(float(row['altitude_deg'])-expected_alt)<=ALTITUDE_BOUND
        culmination=next(row for row in events if row['kind']=='Max')
        # Independent golden-section maximum around the largest sampled altitude.
        lo=indices[maximum]*300-300;hi=indices[maximum]*300+300;ratio=(5**0.5-1)/2
        while hi-lo>0.01:
            a=hi-ratio*(hi-lo);b=lo+ratio*(hi-lo)
            if reference_at(catalog,a)[4]>reference_at(catalog,b)[4]:hi=b
            else:lo=a
        peak=(lo+hi)/2;assert abs(float(culmination['start_ut1_seconds'])-peak)<=1.0
        result['planning']=dict(api=['above_threshold','crossings','culminations'],time_tolerance_seconds=1.0,
            start_ut1_seconds=refined_start,end_ut1_seconds=refined_end,
            interval_ut1=[precise_clock(refined_start),precise_clock(refined_end)],
            erfa_crossings_ut1_seconds=roots,max_crossing_residual_seconds=max(errors),
            maximum_altitude_deg=float(culmination['altitude_deg']),maximum_time_ut1=precise_clock(float(culmination['start_ut1_seconds'])),maximum_time_residual_seconds=abs(float(culmination['start_ut1_seconds'])-peak))
        if (data/'historical-feasibility.csv').exists():
            with (data/'historical-feasibility.csv').open() as f:feasibility=list(csv.DictReader(f))
            for row in feasibility:
                values=np.array([reference_at(catalog,i*300,start=row['date']) for i in range(289)])
                assert abs(float(row['delta_t_start_s'])-values[0,6])<1e-12
                assert abs(float(row['maximum_sampled_altitude_deg'])-max(values[:,4]))<ALTITUDE_BOUND
                assert int(row['selected_count'])==sum(values[:,4]>15)
            result['candidate_feasibility']=feasibility
    (data/'viewing-summary.json').write_text(json.dumps(result,indent=2)+'\n');return result

if __name__=='__main__':
    p=argparse.ArgumentParser(__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--catalog',type=Path,required=True);p.add_argument('--representative',action='store_true');a=p.parse_args()
    print(json.dumps(validate(a.data,a.catalog,a.representative),indent=2))
