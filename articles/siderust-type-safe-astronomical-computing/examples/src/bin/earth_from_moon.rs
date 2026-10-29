use siderust::{
    bodies::solar_system::Moon,
    coordinates::{
        cartesian::Position,
        centers::Selenocentric,
        frames::EclipticMeanJ2000,
        surface::SurfaceSite,
        transform::{AstroContext, SurfaceHorizontalExt},
    },
    ephemeris::{DynEphemeris, RuntimeEphemeris},
    qtty::{Kilometer, DEG, M},
    time::JulianDate,
};

type EarthFromMoon = Position<Selenocentric, EclipticMeanJ2000, Kilometer>;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let path = std::env::args().nth(1).ok_or("BSP path required")?;
    let eph = RuntimeEphemeris::from_bsp(path)?;
    let epoch = JulianDate::new(2_460_000.5); // TT
    let site = SurfaceSite::<Moon>::new(20.0 * DEG, -3.5 * DEG, 0.0 * M)?;
    // Reverse the Moon's geocentric vector: Earth relative to Moon.
    let moon = eph.try_moon_geocentric(epoch)?;
    let (x, y, z) = (-moon.x(), -moon.y(), -moon.z());
    let earth = EarthFromMoon::new(x, y, z);
    let ctx: AstroContext = Default::default();
    let sky = site.observe_position(&earth, &epoch, &ctx)?;
    println!(
        "{} {} {}",
        sky.alt().value(),
        sky.az().value(),
        sky.range().to::<Kilometer>().value()
    );
    Ok(())
}
