//! Beginner example: user-supplied UTC timestamp and terrestrial observing site.
use qtty::{DEG, M};
use siderust::coordinates::{
    centers::Geodetic,
    frames::{EquatorialTrueOfDate, ECEF},
    spherical::Direction,
    transform::SphericalDirectionAstroExt,
};
use tempoch::{JulianDate, Time, TimeContext, JD, TT, UT1, UTC};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<_> = std::env::args().collect();
    if args.len() != 4 {
        return Err("usage: observe UTC_TIMESTAMP LONGITUDE_EAST_DEG LATITUDE_NORTH_DEG".into());
    }
    let lon: f64 = args[2].parse()?;
    let lat: f64 = args[3].parse()?;
    if !lon.is_finite()
        || !lat.is_finite()
        || !(-180.0..=180.0).contains(&lon)
        || !(-90.0..=90.0).contains(&lat)
    {
        return Err("site coordinates are outside their admissible ranges".into());
    }
    let ctx = TimeContext::new();
    let utc = Time::<UTC>::try_from_chrono_with(args[1].parse()?, &ctx)?;
    let tt = utc.to::<TT>().to::<JD>();
    // Introductory geometric scenario: prescribe DUT1 = UT1 - UTC = 0 s.
    // For measured pointing, supply EOP-backed UT1 through a TimeContext.
    let ut1 = JulianDate::<UT1>::new(utc.to_with::<JD>(&ctx)?.try_raw_with(&ctx)?.value());
    let site = Geodetic::<ECEF>::new(lon * DEG, lat * DEG, 0.0 * M);
    // Prescribed true-of-date direction, matching the paper's first application.
    let target = Direction::<EquatorialTrueOfDate>::new(120.0 * DEG, 20.0 * DEG);
    let local = target.to_horizontal_precise(&tt, &ut1, &site);
    println!(
        "altitude={:.6} deg, azimuth={:.6} deg",
        local.polar.value(),
        local.azimuth.value()
    );
    Ok(())
}
