# SPDX-License-Identifier: MIT
from pathlib import Path
import os
import numpy as np, spiceypy as sp, erfa, json,csv,sys
article=Path(__file__).resolve().parents[3]
kernels=Path(os.environ['REPRO_KERNELS'])
sys.path.insert(0,str(article/'scripts'))
r=Path(__file__).resolve().parent;e=Path(os.environ["REPRO_OUTPUT"])
for n in ['pck00011.tpc','naif0012.tls']:sp.furnsh(str(kernels/n))
def basis(lon,lat):
 l,p=np.deg2rad([lon,lat]);return np.array([[-np.sin(l),np.cos(l),0],[-np.sin(p)*np.cos(l),-np.sin(p)*np.sin(l),np.cos(p)],[np.cos(p)*np.cos(l),np.cos(p)*np.sin(l),np.sin(p)]])
def mars(lon,lat,h,k):
 l,p=np.deg2rad([lon,lat]);a,b=3396190.,3376200.;ecc=1-(b/a)**2
 if k==0:
  N=a/np.sqrt(1-ecc*np.sin(p)**2);v=np.array([N*np.cos(p)*np.cos(l),N*np.cos(p)*np.sin(l),N*(1-ecc)*np.sin(p)])
 else:
  u=basis(lon,lat)[2];v=u/np.sqrt((u[0]**2+u[1]**2)/a**2+u[2]**2/b**2)
 normal=v/np.array([a*a,a*a,b*b]);normal/=np.linalg.norm(normal);east=np.array([-np.sin(l),np.cos(l),0]);north=np.cross(normal,east)
 return v+h*normal,np.array([east,north,normal])
def angles(v,b):
 ee,nn,uu=b@v;return [np.rad2deg(np.arctan2(uu,np.hypot(nn,ee))),np.rad2deg(np.arctan2(ee,nn))%360,np.linalg.norm(v),nn,ee,uu]
inputs=[];refs=[]
for s,(lon,lat,h) in enumerate([(0,0,0),(20,-3.5,-100),(-180,45,0),(179.999999,-60,10000),(30,90,0),(-45,-89.999999,10)]):
 b=basis(lon,lat);pos=(1737400+h)*b[2]
 for k,(alt,az) in enumerate([(0,0),(0,90),(0,180),(0,270),(1e-6,45),(-1e-6,225),(90,0),(-90,0)]):
  a,z=np.deg2rad([alt,az]);slant=[1e3,1e6,3.8e8][(s+k)%3];los=slant*(np.cos(a)*np.sin(z)*b[0]+np.cos(a)*np.cos(z)*b[1]+np.sin(a)*b[2]);target=pos+los
  inputs.append([len(inputs),lon,lat,h,*target]);refs.append([alt,az,slant])
for lon,lat in [(0,0),(45,45),(-180,-60),(179.999999,70),(30,90),(-45,-90),(0,89.999999),(137.4,-4.6)]:
 for k in [0,1]:
  for h in [-100,10000]:
   pos,b=mars(lon,lat,h,k);inputs.append([len(inputs),lon,lat,h,k,0,0]);refs.append([*pos,*b.flatten()])
np.savetxt(e/'boundary-input.csv',inputs,delimiter=',',fmt='%.17g')
with (e/'boundary-reference.csv').open('w') as f:
 for i,row in enumerate(refs):f.write(','.join(map(str,[i,*row]))+'\n')
if '--prepare' in sys.argv:sys.exit()
summ={};raw=[]
def stat(name,delta,bound):
 d=np.asarray(delta);assert np.all(np.isfinite(d));assert max(d)<=bound,(name,max(d),bound);summ[name]={'n':len(d),'median':float(np.median(d)),'p95':float(np.percentile(d,95)),'p99':float(np.percentile(d,99)),'max':float(max(d)),'bound':bound};raw.extend([[name,i,float(x)] for i,x in enumerate(d)])
def wrap(a,b):return abs((a-b+180)%360-180)
d=np.loadtxt(e/'rotations.csv',delimiter=',');ref=[]
for jd in d[:,0]:ref.append([erfa.era00(jd,0),erfa.gmst06(jd,0,jd,0),erfa.obl06(jd,0),*erfa.pnm06a(jd,0).flatten()])
ref=np.array(ref);np.savetxt(e/'rotations-reference.csv',np.column_stack([d[:,0],ref]),delimiter=',')
for k,(name,bound) in enumerate([('ERA',2e-11),('GMST',2e-11),('obliquity',1e-14)]):stat(name,abs(d[:,k+1]-ref[:,k]),bound)
stat('BPN',np.max(abs(d[:,4:]-ref[:,3:]),axis=1),2e-12)
from validate_antares import validate
viewing = validate(e, article/'experiments/terrestrial/catalog.json')
d=np.loadtxt(e/'viewing.csv',delimiter=',');ref=np.loadtxt(e/'viewing-reference.csv',delimiter=',')
stat('altitude',abs(d[:,2]-ref[:,0]),3e-11)
stat('azimuth',wrap(d[:,3],ref[:,1]),1e-10)
summ['viewing'] = viewing
from decimal import Decimal,localcontext
D=Decimal.from_float
times=[];time_errors=[[],[],[],[]]
with (e/'utc.csv').open() as f:
 for row in csv.reader(f):
  label=row[0];Y,M,day=map(int,label[:10].split('-'));h,m,s=map(float,label[11:-1].split(':'));u1,u2=erfa.dtf2d('UTC',Y,M,day,int(h),int(m),s);a1,a2=erfa.utctai(u1,u2);t1,t2=erfa.taitt(a1,a2);v=list(map(float,row[1:]));times.append([label,*v,a1,a2,t1,t2])
  time_errors[0].append(abs(v[0]-(a1+a2))*86400);time_errors[1].append(abs(v[1]-(t1+t2))*86400)
  with localcontext() as dc:
   dc.prec=50
   time_errors[2].append(float(abs(D(v[2])+D(v[3])-((D(a1)-Decimal(2451545))+D(a2))*Decimal(86400))))
   time_errors[3].append(float(abs(D(v[4])+D(v[5])-((D(t1)-Decimal(2451545))+D(t2))*Decimal(86400))))
with (e/'utc-reference.csv').open('w') as f:csv.writer(f).writerows(times)
for i,name in enumerate(['UTC_TAI_fullJD','UTC_TT_fullJD','UTC_TAI_split','UTC_TT_split']):stat(name,time_errors[i],50e-6 if i<2 else 1e-6)
# Lunar matrices, directions, finite target: independent CSPICE plus NumPy basis.
mats=[];dirs=[];angs=[];ranges=[];comps=[];jds=[2415020.5,2440000.5,2451545.,2460000.5,2469807.5];sites=[(20,-3.5),(-120,45)]
refs_surface=[]
with (e/'lunar-surface.csv').open() as f:
 for row in csv.reader(f):
  kind=row[0];i,k=map(int,row[1:3]);jd=jds[i];et=sp.unitim((jd-2451545)*86400,'TDT','TDB');R=sp.pxform('IAU_MOON','J2000',et)
  if kind=='matrix':
   expected=R[:,k];actual=np.array(row[3:],float);mats.append(float(max(abs(actual-expected))))
  else:
   lon,lat=sites[k];b=basis(lon,lat)
   if kind=='direction':
    v=np.eye(3)[int(row[3])];expected=angles(R.T@v,b)[:2];actual=np.array(row[4:],float);dirs.append(max(abs(actual[0]-expected[0]),wrap(actual[1],expected[1])))
   else:
    expected=angles(R.T@np.array([3.8e8,1e8,-4e7])-1737400*b[2],b);actual=np.array(row[3:],float);angs.append(max(abs(actual[0]-expected[0]),wrap(actual[1],expected[1])));ranges.append(abs(actual[2]-expected[2]));comps.append(max(abs(actual[3:]-expected[3:])))
  refs_surface.append([kind,i,k,*expected])
# 3 columns per matrix: aggregate per epoch.
stat('lunar_matrix',np.max(np.array(mats).reshape(5,3),axis=1),1e-10);stat('lunar_direction',dirs,2e-8);stat('lunar_finite_angle',angs,2e-8);stat('lunar_range',ranges,1e-3);stat('lunar_components',comps,.1)
with (e/'lunar-surface-reference.csv').open('w') as f:csv.writer(f).writerows(refs_surface)
d=np.loadtxt(e/'mars.csv',delimiter=',');pos=[];bases=[]
for row in d:
 i,k=map(int,row[:2]);lon,lat=[(137.4,-4.6),(45,45)][i];p,b=mars(lon,lat,0,k);pos.append(max(abs(row[2:5]-p)));bases.append(max(abs(row[5:]-b.flatten())))
stat('mars_position',pos,1e-8);stat('mars_basis',bases,1e-14)
bound_d=[];bound_p=[];bound_b=[];zen=0
with (e/'boundaries.csv').open() as f:
 for row in csv.reader(f):
  i=int(row[0]);v=np.array(row[1:],float);expected=np.array(refs[i]);
  if i<48:
   da=abs(v[0]-expected[0]);dr=abs(v[2]-expected[2]);assert dr<2e-6,(i,dr)
   if abs(expected[0])==90:assert v[1]==0;zen+=1;dz=0
   else:dz=wrap(v[1],expected[1])
   bound_d.append(max(da,dz))
  else:bound_p.append(max(abs(v[:3]-expected[:3])));bound_b.append(max(abs(v[3:]-expected[3:])))
stat('boundary_lunar_angles',bound_d,2e-8);stat('boundary_mars_position',bound_p,1e-8);stat('boundary_mars_basis',bound_b,1e-14);summ['boundary_vertical_cases']=zen
(e/'extended-summary.json').write_text(json.dumps(summ,indent=2)+'\n')
with (e/'extended-residuals.csv').open('w') as f:csv.writer(f).writerows([['observable','case','residual'],*raw])
print(json.dumps(summ,indent=2))
