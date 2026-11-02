use affn::cartesian::Position;
use qtty::{unit::Kilometer, DEG, M};
use siderust::{
    bodies::solar_system::Moon,
    coordinates::{
        centers::Geocentric,
        frames::ICRS,
        surface::{
            BodySurfaceModel, LatitudeConvention, PlanetographicLongitudeSense, ReferenceSurface,
            SurfaceSite,
        },
        transform::{try_to_center_with, AstroContext, SurfaceHorizontalExt},
    },
};
use tempoch::{JulianDate, TT};

// Local observer model using the published lunar physics.
#[derive(Clone, Copy, Debug)]
struct SurveyMoon;
impl BodySurfaceModel for SurveyMoon {
    type Center = <Moon as BodySurfaceModel>::Center;
    type FixedFrame = <Moon as BodySurfaceModel>::FixedFrame;
    fn body_name() -> &'static str {
        "SurveyMoon"
    }
    fn default_surface() -> ReferenceSurface {
        Moon::default_surface()
    }
    fn default_latitude_convention() -> LatitudeConvention {
        Moon::default_latitude_convention()
    }
    fn planetographic_longitude_sense() -> PlanetographicLongitudeSense {
        Moon::planetographic_longitude_sense()
    }
}

type Target<B> = Position<<B as BodySurfaceModel>::Center, ICRS, Kilometer>;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let epoch = JulianDate::<TT>::new(2_460_000.5);
    let context = AstroContext::new();
    // Synthetic input for an interface demonstration.
    let geocentric_target = Position::<Geocentric, ICRS, Kilometer>::new(400_000.0, 0.0, 0.0);
    // Check the center shift before observing.
    let target: Target<SurveyMoon> = try_to_center_with(&geocentric_target, epoch, &context)?;
    let site = SurfaceSite::<SurveyMoon>::new(20.0 * DEG, -3.5 * DEG, 0.0 * M)?;
    let observation = site.observe_position(&target, &epoch, &context)?;
    let lunar_site = SurfaceSite::<Moon>::new(20.0 * DEG, -3.5 * DEG, 0.0 * M)?;
    let reference = lunar_site.observe_position(&target, &epoch, &context)?;
    assert_eq!(observation.alt(), reference.alt());
    assert_eq!(observation.az(), reference.az());
    assert_eq!(observation.range(), reference.range());
    Ok(())
}
