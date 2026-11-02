//! Complete geometric Antares grid, with selected samples and crossing brackets.
#[path = "../antares.rs"]
#[allow(dead_code)]
mod antares;
use std::{fs::File, io::Write, path::PathBuf};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut args = std::env::args().skip(1);
    let out = PathBuf::from(
        args.next()
            .ok_or("usage: viewing OUTPUT [--representative]")?,
    );
    let representative = match args.next().as_deref() {
        None => false,
        Some("--representative") => true,
        _ => return Err("usage: viewing OUTPUT [--representative]".into()),
    };
    std::fs::create_dir_all(&out)?;
    let mut grid = File::create(out.join("viewing.csv"))?;
    let mut epochs = File::create(out.join("viewing-epochs.csv"))?;
    writeln!(
        epochs,
        "index,ut1,jd_ut1,jd_tt,ra_true_deg,dec_true_deg,delta_t_seconds"
    )?;
    let mut selected = File::create(out.join("viewing-selected.csv"))?;
    writeln!(selected, "index,ut1,altitude_deg")?;
    let start = antares::START.parse::<chrono::NaiveDateTime>()?;
    let observer = antares::site();
    let mut indices = Vec::new();
    let mut altitudes = Vec::new();
    for i in 0..=288 {
        if representative && i != 0 && i != 144 && i != 288 {
            continue;
        }
        let ut1_label = start + chrono::Duration::seconds(i * 300);
        let sky = antares::observe(ut1_label, &observer)?;
        writeln!(
            grid,
            "{i},{:.17},{:.17},{:.17}",
            sky.tt.raw().value(),
            sky.altitude.value(),
            sky.azimuth.value()
        )?;
        writeln!(
            epochs,
            "{i},{},{:.17},{:.17},{:.17},{:.17},{:.17}",
            ut1_label.format("%Y-%m-%dT%H:%M:%S"),
            sky.ut1.raw().value(),
            sky.tt.raw().value(),
            sky.ra.value(),
            sky.dec.value(),
            sky.delta_t.value()
        )?;
        altitudes.push(sky.altitude);
        if sky.altitude > antares::THRESHOLD {
            indices.push(i);
            writeln!(
                selected,
                "{i},{},{:.17}",
                ut1_label.format("%Y-%m-%dT%H:%M:%S"),
                sky.altitude.value()
            )?;
        }
    }
    let mut spans = File::create(out.join("viewing-spans.csv"))?;
    let mut brackets = File::create(out.join("viewing-brackets.csv"))?;
    writeln!(spans, "first_index,last_index")?;
    writeln!(brackets, "before_index,after_index")?;
    if !representative {
        assert_eq!(altitudes.len(), 289);
        let mut k = 0;
        while k < indices.len() {
            let first = indices[k];
            while k + 1 < indices.len() && indices[k + 1] == indices[k] + 1 {
                k += 1;
            }
            writeln!(spans, "{first},{}", indices[k])?;
            k += 1;
        }
        for i in 0..288 {
            if (altitudes[i] > antares::THRESHOLD) != (altitudes[i + 1] > antares::THRESHOLD) {
                writeln!(brackets, "{i},{}", i + 1)?;
            }
        }
    }
    Ok(())
}
