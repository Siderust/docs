# Historical Antares altitude and planning experiment

The observing day is 1896 July 14 in the proleptic Gregorian calendar on UT1,
from 00:00 through the following 00:00, inclusive. The WGS 84 site retains
geodetic latitude 41.35403 degrees north, longitude 2.15017 degrees east and
prescribed zero ellipsoidal height. Height is not a measured elevation.
The constraint is geometric altitude strictly greater than 15 degrees.

`catalog.json` retains SIMBAD * alf Sco: ICRS at epoch J2000, RA
16h 29m 24.45970s and declination -26d 25m 55.2094s, with source/metadata.
This is a fixed catalog direction. Proper motion and parallax are omitted
in both computations; accumulated catalog motion between 1896 and J2000 is
about 2.7 arcsec. There is no precision historical-pointing claim. Aberration,
light-time, deflection, atmospheric refraction and solar illumination are not
included. The result is an altitude selection, not a nighttime window.

UT1 is constructed directly from naive Gregorian calendar fields. Tempoch's
pinned historical Delta T interpolation supplies TT: approximately -5.788436 s
at the start and -5.786713 s at the end. Negative TT-UT1 is valid for this model.
No modern UTC label or leap-second-table extrapolation is used. The exact
prescription, three table knots, origin/spacing and source checksum are in
catalog.json. The conservative historical model accuracy allowance is +/-15 s,
not a date-specific measured EOP uncertainty or a statistical standard error.
See ../TIME_MODELS.md for the investigation and alternate-date feasibility.

The code applies Siderust's public bias-precession-nutation matrix at TT,
constructs true-of-date geometry and calls to_horizontal_precise with separate
TT and UT1. This direct path avoids the context adapter's redundant UTC/EOP
lookup before UTC existed. No library implementation is changed.

A local HistoricalAntares implements AltitudeProvider with exactly this
geometric function. The released above_threshold, crossings and culminations
APIs operate on TT search intervals, converting back to historical UT1 inside
the provider. SearchOpts::time_tolerance is one second. No apparent-place
correction is introduced by the adapter. The five-minute grid is independently
retained for visualization and sample selection.

## Recorded results

The 289 grid samples contain 56 values above threshold, spanning 18:25--23:00
UT1. The five-minute brackets are 18:20--18:25 and 23:00--23:05 UT1.
The event tools refine the interval to 18:21:22--23:01:55 UT1, rounded to the
nearest second. The refined maximum is 22.440825 degrees at 20:41:39 UT1;
the largest grid sample is 22.439744 degrees at 20:40 UT1.

Independent ERFA uses cal2jd, its own evaluation of the prescribed Delta T
interpolation, pnm06a, gmst06 + ee00(obl06,nut06a.dpsi), and hd2ae. The original
3e-11-degree altitude and 1e-10-degree azimuth bounds are unchanged. Maximum
residuals are 2.41585e-12 and 8.07177e-12 degrees. A separate gst06a diagnostic
also passes these bounds for this day. Independent bisection agrees with
refined crossings to 0.009391 seconds; a separate extremum search checks the
culmination. These numerical comparisons do not validate physical Delta T or
stellar-motion assumptions.

## Replay and regenerate

For this subset only:

```bash
bash experiments/terrestrial/reproduce.sh independent-historical-001
```

For both applications, use ../reproduce.sh as described in ../README.md.
The standalone subset creates an isolated pinned Python environment and Cargo
target directory, checks representative epochs first, then all grid values,
time scales, selections, events, figure/insets and checksums. It needs no EOP
file or ephemeris kernel. No existing run is overwritten.

Regenerate the publication outputs from immutable evidence with
`bash experiments/reproduce.sh --tables tables-001`, as described in the central
guide. The CSV/JSON records distinguish samples, five-minute brackets and refined
planning events. Root tolerance is not inferred from the plotting cadence.
