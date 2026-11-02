//! Fixed-catalog Antares geometry on a historical UT1 observing day.
use qtty::{
    angular::{Degrees, Radians},
    time::Seconds,
    M, SEC,
};
use siderust::{
    astro::{
        nutation::{Iau2006A, NutationModel},
        precession::precession_nutation_matrix,
    },
    coordinates::{
        cartesian,
        centers::Geodetic,
        frames::{EquatorialTrueOfDate, ECEF, ICRS},
        spherical::Direction,
        transform::SphericalDirectionAstroExt,
    },
    event::altitude::AltitudeProvider,
};
use tempoch::{JulianDate, ModifiedJulianDate, Time, TimeContext, JD, TT, UT1};

pub const LONGITUDE: Degrees = Degrees::new(2.15017);
pub const LATITUDE: Degrees = Degrees::new(41.35403);
pub const THRESHOLD: Degrees = Degrees::new(15.0);
pub const START: &str = "1896-07-14T00:00:00"; // Proleptic Gregorian, UT1; never UTC.
                                               // SIMBAD * alf Sco, fixed ICRS direction at epoch J2000, 2007A&A...474..653V.
pub const RA: Degrees = Degrees::new((16.0 + 29.0 / 60.0 + 24.45970 / 3600.0) * 15.0);
pub const DEC: Degrees = Degrees::new(-(26.0 + 25.0 / 60.0 + 55.2094 / 3600.0));

pub fn site() -> Geodetic<ECEF> {
    Geodetic::new(LONGITUDE, LATITUDE, 0.0 * M)
}

pub fn ut1_time(label: chrono::NaiveDateTime) -> Result<Time<UT1>, Box<dyn std::error::Error>> {
    let j2000_label = "2000-01-01T12:00:00".parse::<chrono::NaiveDateTime>()?;
    // Calendar arithmetic only: these labels do not pass through chrono::Utc.
    let elapsed_since_j2000 = label.signed_duration_since(j2000_label).num_seconds() as f64 * SEC;
    Ok(Time::<UT1>::from_raw_j2000_seconds(elapsed_since_j2000)?)
}

pub struct Observation {
    pub tt: JulianDate<TT>,
    pub ut1: JulianDate<UT1>,
    pub delta_t: Seconds,
    pub ra: Degrees,
    pub dec: Degrees,
    pub altitude: Degrees,
    pub azimuth: Degrees,
}

pub fn observe(
    label: chrono::NaiveDateTime,
    observer: &Geodetic<ECEF>,
) -> Result<Observation, Box<dyn std::error::Error>> {
    let ut1 = ut1_time(label)?;
    let tt = ut1.to_with::<TT>(&TimeContext::new())?;
    at_epochs(tt, ut1, observer)
}

pub fn at_epochs(
    tt: Time<TT>,
    ut1: Time<UT1>,
    observer: &Geodetic<ECEF>,
) -> Result<Observation, Box<dyn std::error::Error>> {
    let tt = tt.to::<JD>();
    let ut1 = ut1.to::<JD>();

    let catalog_vector = Direction::<ICRS>::new(RA, DEC).to_cartesian();
    let nutation = Iau2006A::nutation(tt);
    let precession_nutation = precession_nutation_matrix(tt, nutation.dpsi, nutation.deps);
    // Direct public BPN avoids the frame adapter's redundant historical TT -> UTC lookup.
    // BPN rotates a unit catalog vector; retain its normalization and declared output frame.
    let [x, y, z] = precession_nutation.apply_array([
        catalog_vector.x(),
        catalog_vector.y(),
        catalog_vector.z(),
    ]);
    let true_of_date =
        cartesian::Direction::<EquatorialTrueOfDate>::new_unchecked(x, y, z).to_spherical();

    let horizontal = true_of_date.to_horizontal_precise(&tt, &ut1, observer);

    Ok(Observation {
        tt,
        ut1,
        delta_t: tempoch::delta_t_seconds(ut1.raw())?,
        ra: true_of_date.azimuth,
        dec: true_of_date.polar,
        altitude: horizontal.polar,
        azimuth: horizontal.azimuth,
    })
}

/// Adapter for Siderust planning: the same typed observer and geometric model as the grid.
pub struct HistoricalAntares;
impl AltitudeProvider for HistoricalAntares {
    fn altitude_at(&self, observer: &Geodetic<ECEF>, mjd: ModifiedJulianDate<TT>) -> Radians {
        let tt = mjd.to_j2000s();
        let ut1 = tt
            .to_with::<UT1>(&TimeContext::new())
            .expect("historical Delta T coverage");
        // AltitudeProvider is infallible; restrict this adapter to the model coverage.
        at_epochs(tt, ut1, observer)
            .expect("historical provider model coverage")
            .altitude
            .to::<qtty::unit::Radian>()
    }
}
