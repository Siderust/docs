use qtty::{unit, velocity::Velocity, Kilometer, Second};

type Speed = Velocity<unit::Kilometer, unit::Second>;

fn main() {
    let distance = Kilometer::new(1_000.0);
    let elapsed = Second::new(100.0);

    let speed: Speed = distance / elapsed;
    assert_eq!(speed.value(), 10.0);

    // Does not compile: let invalid = distance + elapsed;
}
