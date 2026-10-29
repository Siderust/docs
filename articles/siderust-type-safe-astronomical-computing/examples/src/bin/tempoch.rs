use chrono::Utc;
use tempoch::{Time, JD, MJD, TT, UTC};

fn main() {
    let utc_now = Time::<UTC>::from_chrono(Utc::now());
    let tt_now: Time<TT> = utc_now.to::<TT>();

    println!("TT in JD  : {:.9}", tt_now.to::<JD>());
    println!("TT in MJD : {:.9}", tt_now.to::<MJD>());
}
