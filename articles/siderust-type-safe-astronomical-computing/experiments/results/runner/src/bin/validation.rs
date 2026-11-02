use siderust::{astro::{era::earth_rotation_angle, sidereal::gmst_iau2006, precession::{mean_obliquity_iau2006,precession_nutation_matrix},nutation::{Iau2006A,NutationModel}},bodies::solar_system::{Moon,Mars},coordinates::{cartesian::{Direction,Position},centers::{Selenocentric},frames::{ICRS,MoonIauMeanEarth},surface::{SurfaceSite,LatitudeConvention,BodySurfaceModel},transform::{AstroContext,DirectionAstroExt,SurfaceHorizontalExt}}};
use siderust::qtty::*;
use tempoch::{JulianDate,Time,TimeContext,JD,TT,UT1,UTC,TAI};
use std::{io::Write,fs::File,path::Path};
fn main()->Result<(),Box<dyn std::error::Error>> {
 let out=std::env::args().nth(1).unwrap();let root=Path::new(&out); let ctx:AstroContext=AstroContext::new();let tc=TimeContext::new();
 let mut f=File::create(root.join("rotations.csv"))?;
 for i in 0..1000 {let jd=2451545.-36525.+73.125*i as f64;let tt=JulianDate::<TT>::new(jd);let ut=JulianDate::<UT1>::new(jd);let nut=Iau2006A::nutation(tt);let b=precession_nutation_matrix(tt,nut.dpsi,nut.deps);
 write!(f,"{jd},{},{},{}",earth_rotation_angle(ut).value(),gmst_iau2006(ut,tt).value(),mean_obliquity_iau2006(tt).value())?;for row in b.as_matrix(){for x in row{write!(f,",{x}")?;}}writeln!(f)?; }
 let mut f=File::create(root.join("utc.csv"))?;
 for label in ["1972-01-01T00:00:00Z","1972-06-30T23:59:59Z","1972-06-30T23:59:60Z","1972-07-01T00:00:00Z","1999-01-01T00:00:00Z","2000-01-01T12:00:00Z","2015-06-30T23:59:59Z","2015-06-30T23:59:60Z","2015-07-01T00:00:00Z","2016-12-31T23:59:59Z","2016-12-31T23:59:60Z","2017-01-01T00:00:00Z","2025-01-01T00:00:00Z"] {
 let u=Time::<UTC>::parse_rfc3339_with(label,&tc)?;let a=u.to::<TAI>();let t=u.to::<TT>();let (ah,al)=a.raw_seconds_pair();let(th,tl)=t.raw_seconds_pair();writeln!(f,"{label},{},{},{},{},{},{}",a.to::<JD>().raw().value(),t.to::<JD>().raw().value(),ah.value(),al.value(),th.value(),tl.value())?;}
 let mut f=File::create(root.join("lunar-surface.csv"))?;
 for (i,jd) in [2415020.5,2440000.5,2451545.0,2460000.5,2469807.5].iter().enumerate(){let t=JulianDate::<TT>::new(*jd);
 for axis in 0..3 {let mut v=[0.;3];v[axis]=1.;let d=Direction::<MoonIauMeanEarth>::new_unchecked(v[0],v[1],v[2]).to_frame::<ICRS>(&t);writeln!(f,"matrix,{i},{axis},{},{},{}",d.x(),d.y(),d.z())?;}
 for (s,(lon,lat)) in [(20.,-3.5),(-120.,45.)].iter().enumerate(){let site=SurfaceSite::<Moon>::new(*lon*DEG,*lat*DEG,0.0*M)?;
 for (k,v) in [[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]].iter().enumerate(){let d=Direction::<ICRS>::new_unchecked(v[0],v[1],v[2]);let sky=site.observe_direction(&d,&t,&ctx)?;writeln!(f,"direction,{i},{s},{k},{},{}",sky.alt().value(),sky.az().value())?;}
 let p=Position::<Selenocentric,ICRS,Meter>::new(3.8e8,1.0e8,-4.0e7);let sky=site.observe_position(&p,&t,&ctx)?;let q=sky.position();writeln!(f,"finite,{i},{s},{},{},{},{},{},{}",sky.alt().value(),sky.az().value(),sky.range().value(),q.x().value(),q.y().value(),q.z().value())?;
 }}
 let mut f=File::create(root.join("mars.csv"))?;
 for (i,(lon,lat)) in [(137.4,-4.6),(45.,45.)].iter().enumerate(){for (k,conv) in [LatitudeConvention::Planetographic,LatitudeConvention::Planetocentric].iter().enumerate(){let site=SurfaceSite::<Mars>::with_surface(*lon*DEG,*lat*DEG,0.0*M,Mars::default_surface(),*conv)?;let p=site.observer_position::<Meter>()?;let b=site.enu_basis()?;write!(f,"{i},{k},{},{},{}",p.x().value(),p.y().value(),p.z().value())?;for v in [b.east,b.north,b.up]{for x in v{write!(f,",{x}")?;}}writeln!(f)?;}}
 let mut f=File::create(root.join("boundaries.csv"))?;
 for line in std::fs::read_to_string(root.join("boundary-input.csv"))?.lines(){let v:Vec<f64>=line.split(',').map(|x|x.parse().unwrap()).collect();let id=v[0] as usize;
 if id<48 {let site=SurfaceSite::<Moon>::new(v[1]*DEG,v[2]*DEG,v[3]*M)?;let p=Position::<Selenocentric,MoonIauMeanEarth,Meter>::new(v[4],v[5],v[6]);let sky=site.observe_position(&p,&siderust::J2000,&ctx)?;writeln!(f,"{id},{},{},{}",sky.alt().value(),sky.az().value(),sky.range().value())?;}
 else {let conv=if v[4]==0.{LatitudeConvention::Planetographic}else{LatitudeConvention::Planetocentric};let site=SurfaceSite::<Mars>::with_surface(v[1]*DEG,v[2]*DEG,v[3]*M,Mars::default_surface(),conv)?;let p=site.observer_position::<Meter>()?;let b=site.enu_basis()?;write!(f,"{id},{},{},{}",p.x().value(),p.y().value(),p.z().value())?;for v in [b.east,b.north,b.up]{for x in v{write!(f,",{x}")?;}}writeln!(f)?;}}
 Ok(())
}
