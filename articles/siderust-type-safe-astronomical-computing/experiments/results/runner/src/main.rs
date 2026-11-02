use siderust::{bodies::solar_system::{Earth,Moon},ephemeris::{RuntimeEphemeris,DynEphemeris},time::JulianDate};
use siderust::qtty::Kilometer;
fn main()->Result<(),Box<dyn std::error::Error>> {
 let eph=RuntimeEphemeris::from_bsp(std::env::args().nth(1).unwrap())?;
 println!("jd,ex,ey,ez,mx,my,mz,ax,ay,az,lx,ly,lz");
 for i in 0..1000 {
  let j=2451545.0+8.0*i as f64; let t=JulianDate::new(j);
  let e=eph.try_earth_heliocentric(t)?; let m=eph.try_moon_geocentric(t)?;
  let a=Earth::vsop87a(t); let l=Moon::get_geo_position::<Kilometer>(t);
  println!("{j},{},{},{},{},{},{},{},{},{},{},{},{}",e.x().value(),e.y().value(),e.z().value(),m.x().value(),m.y().value(),m.z().value(),a.x().value(),a.y().value(),a.z().value(),l.x().value(),l.y().value(),l.z().value());
 } Ok(())
}
