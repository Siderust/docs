use qtty::{unit, velocity::Velocity, KM, SEC};

type Speed = Velocity<unit::Kilometer, unit::Second>;

fn main() {
    let distance = 1_000.0 * KM;
    let elapsed = 100.0 * SEC;

    let speed: Speed = distance / elapsed;
    assert_eq!(speed, Speed::new(10.0));

    // Does not compile: let invalid = distance + elapsed;
}
