//! Geometric Antares pointing; defaults reproduce the paper's terrestrial site.
#[path = "../antares.rs"]
#[allow(dead_code)]
mod antares;
use qtty::{angular::Degrees, DEG, M};
use siderust::coordinates::{centers::Geodetic, frames::ECEF};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<_> = std::env::args().skip(1).collect();
    let (ut1_label, observer) = match args.as_slice() {
        [] => (antares::START.parse()?, antares::site()),
        [label, longitude, latitude] => {
            let longitude = Degrees::new(longitude.parse()?);
            let latitude = Degrees::new(latitude.parse()?);
            if !longitude.is_finite()
                || !latitude.is_finite()
                || longitude < -180.0 * DEG
                || longitude > 180.0 * DEG
                || latitude < -90.0 * DEG
                || latitude > 90.0 * DEG
            {
                return Err("site coordinates are outside their admissible ranges".into());
            }
            (
                label.parse()?,
                Geodetic::<ECEF>::new(longitude, latitude, 0.0 * M),
            )
        }
        _ => {
            return Err(
                "usage: observe [UT1_CALENDAR_LABEL LONGITUDE_EAST_DEG LATITUDE_NORTH_DEG]".into(),
            )
        }
    };

    let observation = antares::observe(ut1_label, &observer)?;
    println!(
        "Antares: altitude={:.6}, azimuth={:.6}",
        observation.altitude, observation.azimuth
    );
    Ok(())
}
