use tempoch::{JulianDate,TT};fn main(){let t=JulianDate::<TT>::new(2451545.);let _=siderust::astro::sidereal::gmst_iau2006(t,t);}
