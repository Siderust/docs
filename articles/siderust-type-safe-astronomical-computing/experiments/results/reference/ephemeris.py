# SPDX-License-Identifier: MIT
from pathlib import Path
import os,sys
import numpy as np, spiceypy as sp, erfa, json, re, hashlib
root=Path(__file__).resolve().parent
article=Path(__file__).resolve().parents[3]
kernels=Path(os.environ['REPRO_KERNELS'])
sys.path.insert(0,str(article/'scripts'))

output_dir=Path(os.environ["REPRO_OUTPUT"])
for n in ['de440s.bsp','pck00011.tpc','naif0012.tls']:sp.furnsh(str(kernels/n))
d=np.genfromtxt(output_dir/'ephemeris.csv',delimiter=',',names=True)
C=erfa.ecm06(2451545.,0.)
ref=[]
for j in d['jd']:
 et=sp.unitim((j-2451545)*86400.,'TDT','TDB')
 e=C@sp.spkpos('EARTH',et,'J2000','NONE','SUN')[0]/149597870.7
 m=C@sp.spkpos('MOON',et,'J2000','NONE','EARTH')[0]
 ref.append([j,*e,*m])
ref=np.array(ref);np.savetxt(output_dir/'reference.csv',ref,delimiter=',',header='jd,ex,ey,ez,mx,my,mz')
summary={}
for name,cols,rcols in [('Earth model',['ax','ay','az'],slice(1,4)),('Moon model',['lx','ly','lz'],slice(4,7)),('Earth SPK',['ex','ey','ez'],slice(1,4)),('Moon SPK',['mx','my','mz'],slice(4,7))]:
 v=np.column_stack([d[c] for c in cols]);delta=np.linalg.norm(v-ref[:,rcols],axis=1)
 np.savetxt(output_dir/f'{name.replace(" ","-")}-residuals.csv',np.column_stack([d['jd'],delta]),delimiter=',',header='jd,residual')
 summary[name]=dict(zip(['median','p95','p99','max'],[float(x) for x in [np.median(delta),*np.percentile(delta,[95,99]),max(delta)]]))
# Independently evaluate the featured lunar application under its declared time model.
from validate_lunar_application import validate as validate_lunar
summary['lunar'] = validate_lunar(output_dir, kernels, article/'experiments/lunar/inputs.json')
# Independently regenerate the complete fixed-catalog Antares reference.
from validate_antares import validate
summary['figure'] = validate(output_dir, article/'experiments/terrestrial/catalog.json')
summary['versions']={'pyerfa':erfa.__version__,'erfa':erfa.version.erfa_version,'spiceypy':sp.__version__,'cspice':sp.tkvrsn('TOOLKIT'),'numpy':np.__version__}
summary['kernels_sha256']={name:hashlib.sha256((kernels/name).read_bytes()).hexdigest() for name in ['de440s.bsp','naif0012.tls','pck00011.tpc']}
(output_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
assert summary['Earth SPK']['max']<2e-12
assert summary['Moon SPK']['max']<2e-4
assert max(summary['lunar']['absolute_residuals'][:2])<3e-9
assert summary['lunar']['absolute_residuals'][2]<2e-8
assert summary['figure']['max_altitude_difference_deg']<1e-8
