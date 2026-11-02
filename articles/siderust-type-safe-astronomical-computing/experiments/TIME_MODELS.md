# Time-scale investigation for the two applications

## Historical terrestrial day

Both proposed dates were executed on a complete 289-epoch UT1 grid and
independently checked with ERFA. The 1896 July 14 case gives starting Delta T
-5.788436234639996 s, maximum sampled altitude 22.439744112062407 degrees and
56 selected samples. The 1936 July 19 case gives +23.78090349075975 s,
22.350105856684777 degrees and 56 samples. Both are technically feasible and
astronomically suitable. The preferred 1896 date was retained because the
pinned historical model and transformation APIs support it directly; the
alternative offers no necessary technical or reproducibility advantage.
No historical interpretation of the chosen parameters is needed for the model.

The calendar is proleptic Gregorian. Chrono NaiveDateTime is used only for
calendar arithmetic; it never produces a chrono::Utc value. The UT1 axis is
constructed directly from exact integer J2000 seconds, and Tempoch's
Time<UT1>::to_with::<TT> relates it to TT. No pre-definition UTC policy or
backward extrapolation of a leap-second table is enabled. Negative TT-UT1
for this date is a valid output of the adopted historical prescription.

Tempoch-core 0.11.2 uses the Meeus biennial Delta T table, anchored at
JD 2312752.5 with step 730.5 days and three-point interpolation. For index i,
let n be the offset from that knot in steps, a=y[i+1]-y[i], b=y[i+2]-y[i+1].
The prescribed value is y[i]+n*a+n*(n-1)*(b-a)/2. The selected day uses i=138
and [-6.1,-4.7,-2.7] seconds; the alternative uses i=158 and [23.7,24.0,24.3].
These are the implementation's exact JD knots, not inferred Gregorian dates.
The source path, version and SHA-256 are pinned in terrestrial/catalog.json.
The independent Python reference evaluates the documented interpolation from
that metadata and uses ERFA cal2jd for its independent UT1 grid. It does not
consume Rust TT or altitude values as its expected time/geometry oracle.

The pinned UT1 scale documentation gives an approximately +/-15-second
historical-model accuracy allowance. This broad conservative allowance is
retained explicitly, not relabeled as a measured 1896 EOP error or a statistical
one-sigma uncertainty. Published telescopic-era Delta T estimates can be more
precise, but replacing the pinned model was unnecessary for this fixed-model
software experiment. Numerical agreement with ERFA does not validate the
physical Delta T estimate. The numerical one-second event-search tolerance
likewise is not a claim of one-second physical observing-time accuracy.

The context-based ICRS-to-true frame adapter in the evaluated release queries
EOP by converting TT to UTC, even when NullEop ultimately supplies zeros.
The historical workflow avoids that redundant route: it directly applies the
public IAU 2006/2000A BPN operation and then the typed true-of-date horizontal
interface with explicit TT and UT1. A local AltitudeProvider exposes exactly
that function to above_threshold, crossings and culminations. Their search
axis is TT; inside the adapter the same historical model returns UT1. No
library implementation is modified. Source-level native UTC conversion
restrictions therefore do not block the preferred historical date.

Fixed J2000 catalog coordinates, with no proper motion/parallax, remain a
shared model assumption. Catalog motion would accumulate about 2.7 arcsec
between 1896 and J2000. This limits physical historical-pointing interpretation,
independently of precession/nutation precision and numerical root agreement.
Neither solar illumination nor nighttime observability is inferred.

## Independent lunar TT epoch

The lunar epoch is exactly 2017-10-01 17:14:00 TT. TT midnight is JD 2458027.5;
62040 within-day seconds are added in native split J2000-second storage,
producing 560150040 TT seconds. There is no UTC conversion and no historical
Delta T dependency. The observing coordinates are exactly 20.17 degrees east,
-1.10 degrees planetocentric, with zero height on the 1737.4 km sphere.

The released RuntimeEphemeris path collapses input TT to a full Julian date
before constructing its SPICE-style time argument. The application instead
uses the existing public SpkKernel evaluator with explicit TDB seconds, then
constructs the typed selenocentric ICRS position. This preserves native input
epoch precision without modifying the library. Segment frame/center/type
metadata and actual coverage are checked, in addition to the pinned kernel's
producer provenance. The change is an application adapter, not a general claim
that a raw SPK frame ID certifies physical frame realization.

Tempoch's TT-to-TDB conversion is the seven-term approximation from USNO
Circular 179, with a documented accuracy of order 10 microseconds over
1600--2200. The primary application uses that same prescribed TDB argument for
SPK evaluation and analytical IAU_MOON orientation. Independent Python evaluates
the formula directly from TT calendar fields and supplies the independently
derived TDB seconds to CSPICE. All three NAIF input files are hash-pinned.
Angles, range, center altitude, inertial/fixed/relative/horizontal vectors,
surface position and rotation matrix are compared, with the retained bounds.

For transparency, native CSPICE unitim(TT,TDT,TDB) is also evaluated. At this
epoch it differs from the seven-term convention by 14.6627 microseconds and
changes the final range by about 0.8 mm. That diagnostic exceeds the original
20-micrometre matched-convention range criterion; it is not declared passing.
The primary result tests numerical geometry under the explicit common time
prescription, not physical accuracy at the micrometre level. The independent
reference never imports the Rust time result as an expected value. No tolerance
has been widened, and the astronomical orientation/surface model is unchanged.
