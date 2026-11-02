//! Complete intermediate geometry for the independent CSPICE comparison.
#[path = "../lunar_application.rs"]
mod lunar_application;
use std::{fs::File, io::Write, path::PathBuf};
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut args = std::env::args().skip(1);
    let bsp = args.next().ok_or("usage: lunar_geometry BSP OUTPUT")?;
    let out = PathBuf::from(args.next().ok_or("OUTPUT required")?);
    std::fs::create_dir_all(&out)?;
    let g = lunar_application::evaluate(&bsp)?;
    // The CSV schema fixes each frame and unit; extract scalars only at this boundary.
    let mut f = File::create(out.join("lunar-application.csv"))?;
    writeln!(f, "quantity,x,y,z")?;
    for (name, v) in [
        ("inertial_km", g.inertial.as_array()),
        ("fixed_km", g.fixed.as_array()),
        ("observer_km", g.observer.as_array()),
        ("relative_km", g.relative.as_array()),
        ("horizontal_km", g.observation.position().as_array()),
    ] {
        let [x, y, z] = v.map(|component| component.value());
        writeln!(f, "{name},{x:.17},{y:.17},{z:.17}")?;
    }
    for (i, v) in g.rotation.iter().enumerate() {
        writeln!(f, "rotation_{i},{:.17},{:.17},{:.17}", v[0], v[1], v[2])?;
    }
    let altitude = g.observation.alt().value();
    let azimuth = g.observation.az().value();
    let range = g.observation.range().value();
    for (name, value) in [
        ("tt_seconds", g.tt_seconds.value()),
        ("tdb_seconds", g.tdb_seconds.value()),
        ("tt_jd", g.tt_jd.raw().value()),
        ("altitude_deg", altitude),
        ("azimuth_deg", azimuth),
        ("range_km", range),
        ("center_altitude_deg", g.center_altitude.value()),
        ("parallax_deg", g.parallax.value()),
        ("coverage_start_et", g.coverage_start.value()),
        ("coverage_end_et", g.coverage_end.value()),
    ] {
        writeln!(f, "{name},{value:.17},,")?;
    }
    std::fs::write(
        out.join("lunar.txt"),
        format!("{:.17} {:.17} {:.17}\n", altitude, azimuth, range),
    )?;
    Ok(())
}
