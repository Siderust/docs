use siderust::ephemeris::{DynEphemeris, RuntimeEphemeris};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let path = std::env::args()
        .nth(1)
        .unwrap_or_else(|| "kernels/de440.bsp".to_owned());
    let eph = RuntimeEphemeris::from_bsp(path)?;
    let jd = siderust::time::J2000;

    let earth = eph.try_earth_heliocentric(jd)?;
    let moon = eph.try_moon_geocentric(jd)?;
    println!("Earth: {earth}; Moon: {moon}");
    Ok(())
}
