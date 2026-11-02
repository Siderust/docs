# Earth from a lunar surface observer

The hypothetical site is exactly 20.17 degrees east longitude and -1.10 degrees
planetocentric latitude, at zero height on the 1737.4 km lunar reference sphere.
The epoch is exactly 2017 October 1, 17:14:00 TT. It is not interpreted as UTC.
The epoch is constructed from TT midnight plus 62040 seconds, retaining native
split storage rather than first collapsing the date to a floating-point JD.

Siderust parses the pinned DE440s SPK, validates Earth/Moon segment metadata and
coverage, evaluates the finite Earth-relative-to-Moon state with explicit TDB
seconds, and constructs Position<Selenocentric,ICRS,Kilometer>. SurfaceSite<Moon>
and observe_position use the established analytical MoonIauMeanEarth / IAU_MOON
orientation and spherical reference surface. No principal-axes/binary-PCK model,
refraction, aberration, light-time or terrain correction is substituted.

Both ephemeris and analytical orientation use Tempoch's seven-term USNO Circular
179 TT-to-TDB prescription. The independent Python reference evaluates that
prescription from the specified TT calendar fields, then calls CSPICE spkpos
and pxform at that TDB argument. It constructs its own surface position and
north/east/up basis. Rust results are never the expected geometry oracle.
The chosen epoch lies within the actual Earth and Moon kernel coverage.

The maximum application angle residual is 9.0239e-12 degrees and range residual
5.8208e-11 km, below the retained 3e-9-degree and 2e-8-km bounds. Full inertial,
body-fixed, observer-relative and horizontal vectors and the rotation matrix
are compared too. The maximum component residual is 6.1461e-8 km (about 0.062 mm),
within the existing 0.1 m surface-test component criterion; rotation residual is
1.2635e-13, within 1e-10. These are numerical agreement checks, not a physical
uncertainty budget for the orientation, surface or TT-to-TDB model.

Results: altitude 64.753217 degrees; azimuth 271.106519 degrees (north through
east); range 391056.058 km; Moon-center altitude 64.861355 degrees; observer
parallax contribution 0.10814 degrees. Exact numbers are in the recorded CSV/JSON.

A separate native CSPICE unitim diagnostic differs by about 14.66 microseconds
in dynamical time and about 0.8 mm in final range; it does not satisfy the
20-micrometre matched-convention range criterion. This is an explicitly retained
time-model difference, not reported as a passing test. No tolerance or library
code was altered to hide it. See ../TIME_MODELS.md.

Replay both applications with `bash experiments/reproduce.sh RUN_ID [KERNEL_DIR]`
from the article directory. Missing NAIF inputs are fetched from the URLs in
inputs.json and checked against fixed SHA-256 values. The full suite uses the same verified inputs. The replay verifies all recorded geometry
and regenerates lunar macros without changing the independent lunar/Mars
regression populations or unrelated experimental data.
