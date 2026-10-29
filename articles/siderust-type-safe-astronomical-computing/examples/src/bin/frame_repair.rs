use qtty::unit::Kilometer;
use siderust::{
    coordinates::{
        cartesian::Position,
        centers::Geocentric,
        frames::{EclipticMeanJ2000, ICRS},
        transform::PositionAstroExt,
    },
    J2000,
};

type Equatorial = Position<Geocentric, ICRS, Kilometer>;
type Ecliptic = Position<Geocentric, EclipticMeanJ2000, Kilometer>;

fn main() {
    let equatorial = Equatorial::new(1.0, 2.0, 3.0);
    let ecliptic = Ecliptic::new(1.0, 2.0, 3.0);
    // equatorial - ecliptic is rejected: the frame markers differ.
    let aligned = ecliptic.to_frame::<ICRS>(&J2000);
    let displacement = equatorial - aligned;
    assert!(displacement.x().value().is_finite());
}
