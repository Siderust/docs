//! Explicit kernel input and a typed TT epoch.
use siderust::ephemeris::{DynEphemeris, RuntimeEphemeris};
use tempoch::{JulianDate, TT};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let bsp_path = std::env::args_os()
        .nth(1)
        .ok_or("usage: runtime_ephemeris BSP_KERNEL")?;
    let ephemeris = RuntimeEphemeris::from_bsp(bsp_path)?;
    let epoch: JulianDate<TT> = siderust::time::J2000;

    let earth = ephemeris.try_earth_heliocentric(epoch)?;
    let moon = ephemeris.try_moon_geocentric(epoch)?;
    println!("Earth: {earth}; Moon: {moon}");
    Ok(())
}
