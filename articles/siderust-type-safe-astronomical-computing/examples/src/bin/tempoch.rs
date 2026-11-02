use chrono::Utc;
use tempoch::{Time, JD, MJD, TT, UTC};

fn main() {
    let utc_epoch = Time::<UTC>::from_chrono(Utc::now());
    let tt_epoch: Time<TT> = utc_epoch.to::<TT>();

    println!("TT in JD  : {:.9}", tt_epoch.to::<JD>());
    println!("TT in MJD : {:.9}", tt_epoch.to::<MJD>());
}
