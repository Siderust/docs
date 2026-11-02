//! Independent-reference diagnostics for the implemented sidereal convention.
#[path = "../antares.rs"]
#[allow(dead_code)]
mod antares;
use siderust::astro::{
    nutation::{Iau2006A, NutationModel},
    sidereal::{gast_iau2006, gmst_iau2006},
};
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let start = antares::START.parse::<chrono::NaiveDateTime>()?;
    println!("index,jd_ut1,jd_tt,gmst,gast,dpsi,epsa");
    let observer = antares::site();
    for i in 0..=288 {
        let s = antares::observe(start + chrono::Duration::seconds(i * 300), &observer)?;
        let n = Iau2006A::nutation(s.tt);
        println!(
            "{i},{:.17},{:.17},{:.17},{:.17},{:.17},{:.17}",
            s.ut1.raw().value(),
            s.tt.raw().value(),
            gmst_iau2006(s.ut1, s.tt).value(),
            gast_iau2006(s.ut1, s.tt, n.dpsi, n.mean_obliquity).value(),
            n.dpsi.value(),
            n.mean_obliquity.value()
        );
    }
    Ok(())
}
