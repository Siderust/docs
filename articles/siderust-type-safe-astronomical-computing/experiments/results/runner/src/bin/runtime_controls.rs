use siderust::{bodies::solar_system::Moon,coordinates::{cartesian::{Direction,Position},centers::{Geodetic,Topocentric},frames::{ICRS,ECEF},surface::SurfaceSite,transform::{AstroContext,SurfaceHorizontalExt,horizontal_observation_to_direction}}};
use qtty::{DEG,M,unit::Meter};
fn main(){
 let a=Geodetic::<ECEF>::new(0.*DEG,0.*DEG,0.*M);let b=Geodetic::<ECEF>::new(1.*DEG,0.*DEG,0.*M);
 let p=Position::<Topocentric,ICRS,Meter>::new_with_params(a,1.,2.,3.);let same=Position::<Topocentric,ICRS,Meter>::new_with_params(a,2.,3.,4.);let other=Position::<Topocentric,ICRS,Meter>::new_with_params(b,2.,3.,4.);
 assert!(p.checked_sub(&same).is_ok());assert!(p.checked_sub(&other).is_err());
 assert!(SurfaceSite::<Moon>::new(f64::NAN*DEG,0.*DEG,0.*M).is_err());assert!(SurfaceSite::<Moon>::new(0.*DEG,91.*DEG,0.*M).is_err());assert!(SurfaceSite::<Moon>::new(0.*DEG,0.*DEG,-1737400.*M).is_err());
 let site=SurfaceSite::<Moon>::new(0.*DEG,0.*DEG,0.*M).unwrap();let other=SurfaceSite::<Moon>::new(1.*DEG,0.*DEG,0.*M).unwrap();let ctx:AstroContext=AstroContext::new();let t=siderust::J2000;
 for v in [[0.,0.,0.],[f64::NAN,0.,0.]]{assert!(site.observe_direction(&Direction::<ICRS>::new_unchecked(v[0],v[1],v[2]),&t,&ctx).is_err());}
 let d=Direction::<ICRS>::new_unchecked(1.,0.,0.);let sky=site.observe_direction(&d,&t,&ctx).unwrap();let good:Result<Direction<ICRS>,_>=horizontal_observation_to_direction(&sky,&site,&t,&ctx);let bad:Result<Direction<ICRS>,_>=horizontal_observation_to_direction(&sky,&other,&t,&ctx);assert!(good.is_ok());assert!(bad.is_err());println!("All runtime controls passed");
}
