//! Earth from a lunar surface site at 2017-10-01 17:14:00 TT.
#[path = "../lunar_application.rs"]
#[allow(dead_code)]
mod lunar_application;
use siderust::coordinates::transform::{AstroContext, SurfaceHorizontalExt};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let kernel_path = std::env::args_os()
        .nth(1)
        .ok_or("DE440s BSP path required")?;

    // Split TT epoch -> TDB seconds -> checked DE440s selenocentric position.
    let target = lunar_application::target(&kernel_path)?;
    // Shared site: 20.17 E, -1.10 planetocentric, zero height.
    // Moon selects analytical IAU_MOON and the 1737.4 km sphere.
    let site = lunar_application::site()?;
    let context = AstroContext::new();
    let observation = site.observe_position(&target.earth, &target.epoch, &context)?;

    println!(
        "altitude={}, azimuth={}, range={}",
        observation.alt(),
        observation.az(),
        observation.range()
    );
    Ok(())
}
