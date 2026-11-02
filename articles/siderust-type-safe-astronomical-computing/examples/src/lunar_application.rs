//! Typed Earth geometry for the specified TT epoch and lunar surface site.
use affn::Displacement;
use siderust::{
    bodies::solar_system::Moon,
    coordinates::{
        cartesian::{Direction, Position},
        centers::Selenocentric,
        frames::{MoonIauMeanEarth, ICRS},
        surface::{SurfaceError, SurfaceSite},
        transform::{
            AstroContext, DirectionAstroExt, HorizontalObservation, PositionAstroExt,
            SurfaceHorizontalExt,
        },
    },
    formats::spice::SpkKernel,
    qtty::{Degrees, Kilometer, Seconds, M, SEC},
};
use std::path::Path;
use tempoch::{JulianDate, Time, JD, TDB, TT};

pub const LONGITUDE: Degrees = Degrees::new(20.17);
pub const LATITUDE: Degrees = Degrees::new(-1.10);
const EARTH_ID: i32 = 399;
const MOON_ID: i32 = 301;
const EARTH_MOON_BARYCENTER_ID: i32 = 3;

pub type EarthPosition = Position<Selenocentric, ICRS, Kilometer>;
pub type MoonFixedPosition = Position<Selenocentric, MoonIauMeanEarth, Kilometer>;

pub fn site() -> Result<SurfaceSite<Moon>, SurfaceError> {
    SurfaceSite::new(LONGITUDE, LATITUDE, 0.0 * M)
}

pub fn epoch() -> Result<Time<TT>, Box<dyn std::error::Error>> {
    // 2017-10-01 00:00 TT = JD 2458027.5; 17:14:00 = 62040 SI seconds.
    // Retain calendar day and clock seconds separately, without a UTC conversion.
    Ok(Time::<TT>::try_from_raw_j2000_seconds_split(
        ((2_458_027.5 - 2_451_545.0) * 86_400.0) * SEC,
        62_040.0 * SEC,
    )?)
}

/// Diagnostic geometry retains frames, centers and units until CSV serialization.
pub struct Geometry {
    pub tt_seconds: Seconds,
    pub tdb_seconds: Seconds,
    pub tt_jd: JulianDate<TT>,
    pub inertial: EarthPosition,
    pub fixed: MoonFixedPosition,
    pub observer: MoonFixedPosition,
    pub relative: Displacement<MoonIauMeanEarth, Kilometer>,
    pub observation: HorizontalObservation<Moon, Kilometer>,
    pub rotation: [[f64; 3]; 3],
    pub center_altitude: Degrees,
    pub parallax: Degrees,
    pub coverage_start: Seconds,
    pub coverage_end: Seconds,
}

pub struct LunarTarget {
    pub time: Time<TT>,
    pub epoch: JulianDate<TT>,
    pub earth: EarthPosition,
    pub tdb_seconds: Seconds,
    pub coverage_start: Seconds,
    pub coverage_end: Seconds,
}

pub fn target(path: impl AsRef<Path>) -> Result<LunarTarget, Box<dyn std::error::Error>> {
    let time = epoch()?;
    let tdb_seconds = time.to::<TDB>().to_j2000s().raw();
    let epoch = time.to::<JD>();

    let kernel = SpkKernel::open(path)?;
    // DE440s provenance establishes ICRF; a raw SPK frame ID alone does not.
    let earth_moon_segments: Vec<_> = kernel
        .segments()
        .iter()
        .filter(|segment| segment.target == MOON_ID || segment.target == EARTH_ID)
        .collect();
    if ![EARTH_ID, MOON_ID].iter().all(|id| {
        earth_moon_segments
            .iter()
            .any(|segment| segment.target == *id)
    }) || earth_moon_segments.iter().any(|segment| {
        segment.frame_id != 1
            || segment.center != EARTH_MOON_BARYCENTER_ID
            || segment.data_type != 2
            || !segment.start_tdb_seconds.is_finite()
            || !segment.end_tdb_seconds.is_finite()
            || segment.start_tdb_seconds > segment.end_tdb_seconds
    }) {
        return Err("DE440s Earth/Moon metadata mismatch".into());
    }

    let coverage_start = earth_moon_segments
        .iter()
        .map(|segment| Seconds::new(segment.start_tdb_seconds))
        .fold(Seconds::NEG_INFINITY, Seconds::max);
    let coverage_end = earth_moon_segments
        .iter()
        .map(|segment| Seconds::new(segment.end_tdb_seconds))
        .fold(Seconds::INFINITY, Seconds::min);
    if tdb_seconds < coverage_start || tdb_seconds > coverage_end {
        return Err("epoch outside kernel coverage".into());
    }

    // Raw scalars occur only at this SPK interface; assign the checked realization explicitly.
    let state = kernel.state(EARTH_ID, MOON_ID, tdb_seconds.value())?;
    let earth = EarthPosition::new(state[0], state[1], state[2]);
    if !earth.is_finite() {
        return Err("nonfinite Earth position".into());
    }

    Ok(LunarTarget {
        time,
        epoch,
        earth,
        tdb_seconds,
        coverage_start,
        coverage_end,
    })
}

pub fn evaluate(path: impl AsRef<Path>) -> Result<Geometry, Box<dyn std::error::Error>> {
    let LunarTarget {
        time,
        epoch,
        earth,
        tdb_seconds,
        coverage_start,
        coverage_end,
    } = target(path)?;
    let (tt_high, tt_low) = time.raw_seconds_pair();
    let site = site()?;
    let context = AstroContext::new();
    let observation = site.observe_position(&earth, &epoch, &context)?;

    let earth_fixed = earth.to_frame::<MoonIauMeanEarth>(&epoch);
    let observer_fixed = site.observer_position::<Kilometer>()?;
    let relative = earth_fixed - observer_fixed;

    let center_direction = earth.direction().ok_or("degenerate Earth direction")?;
    let center_observation = site.observe_direction(&center_direction, &epoch, &context)?;

    let mut rotation = [[0.; 3]; 3];
    for j in 0..3 {
        let mut axis = [0.; 3];
        axis[j] = 1.;
        let rotated_axis =
            Direction::<ICRS>::new(axis[0], axis[1], axis[2]).to_frame::<MoonIauMeanEarth>(&epoch);
        rotation[0][j] = rotated_axis.x();
        rotation[1][j] = rotated_axis.y();
        rotation[2][j] = rotated_axis.z();
    }

    let center_altitude = center_observation.alt();
    let parallax = center_altitude - observation.alt();

    Ok(Geometry {
        tt_seconds: tt_high + tt_low,
        tdb_seconds,
        tt_jd: epoch,
        inertial: earth,
        fixed: earth_fixed,
        observer: observer_fixed,
        relative,
        observation,
        rotation,
        center_altitude,
        parallax,
        coverage_start,
        coverage_end,
    })
}
