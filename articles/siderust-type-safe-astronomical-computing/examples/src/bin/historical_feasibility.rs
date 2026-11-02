//! Technical feasibility of the two candidate UT1 observing days.
#[path = "../antares.rs"]
#[allow(dead_code)]
mod antares;
use qtty::angular::Degrees;
fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("date,delta_t_start_s,maximum_sampled_altitude_deg,selected_count");
    let observer = antares::site();
    for label in ["1896-07-14T00:00:00", "1936-07-19T00:00:00"] {
        let start = label.parse::<chrono::NaiveDateTime>()?;
        let mut maximum = Degrees::NEG_INFINITY;
        let mut selected = 0;
        for i in 0..=288 {
            let sky = antares::observe(start + chrono::Duration::seconds(i * 300), &observer)?;
            maximum = maximum.max(sky.altitude);
            if sky.altitude > antares::THRESHOLD {
                selected += 1;
            }
        }
        println!(
            "{label},{:.17},{:.17},{selected}",
            antares::observe(start, &observer)?.delta_t.value(),
            maximum.value()
        );
    }
    Ok(())
}
