//! Refined geometric altitude intervals using the released Siderust planning API.
#[path = "../antares.rs"]
#[allow(dead_code)]
mod antares;
use qtty::time::Seconds;
use siderust::event::altitude::{above_threshold, crossings, culminations, SearchOpts};
use std::{fs::File, io::Write, path::PathBuf};
use tempoch::{Interval, Time, TimeContext, MJD, TT, UT1};

fn seconds_ut1(tt: Time<TT, MJD>, base: Time<UT1>) -> Result<Seconds, Box<dyn std::error::Error>> {
    let ut = tt.to_with::<UT1>(&TimeContext::new())?;
    let (h, l) = ut.raw_seconds_pair();
    let (b, c) = base.raw_seconds_pair();
    Ok((h - b) + (l - c))
}
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let out = PathBuf::from(
        std::env::args()
            .nth(1)
            .ok_or("usage: viewing_events OUTPUT")?,
    );
    std::fs::create_dir_all(&out)?;
    let start = antares::START.parse::<chrono::NaiveDateTime>()?;
    let base = antares::ut1_time(start)?;
    let end = antares::ut1_time(start + chrono::Duration::days(1))?;
    let tc = TimeContext::new();
    let window = Interval::try_new(
        base.to_with::<TT>(&tc)?.to::<MJD>(),
        end.to_with::<TT>(&tc)?.to::<MJD>(),
    )?;
    let site = antares::site();
    let opts = SearchOpts {
        time_tolerance: qtty::time::Seconds::new(1.0).to::<qtty::unit::Day>(),
    };
    let target = antares::HistoricalAntares;
    let mut f = File::create(out.join("viewing-events.csv"))?;
    writeln!(f, "kind,start_ut1_seconds,end_ut1_seconds,altitude_deg")?;
    for period in above_threshold(&target, &site, window, antares::THRESHOLD, opts) {
        writeln!(
            f,
            "interval,{:.9},{:.9},",
            seconds_ut1(period.start, base)?.value(),
            seconds_ut1(period.end, base)?.value()
        )?;
    }
    for event in crossings(&target, &site, window, antares::THRESHOLD, opts) {
        writeln!(
            f,
            "{},{:.9},,",
            event.direction,
            seconds_ut1(event.mjd, base)?.value()
        )?;
    }
    for event in culminations(&target, &site, window, opts) {
        writeln!(
            f,
            "{:?},{:.9},,{:.17}",
            event.kind,
            seconds_ut1(event.mjd, base)?.value(),
            event.altitude.value()
        )?;
    }
    Ok(())
}
