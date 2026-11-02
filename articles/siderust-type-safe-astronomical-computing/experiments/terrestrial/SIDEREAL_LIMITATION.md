# Sidereal formulation diagnostic

The evaluated release uses GMST plus the IAU 2000 equation of equinoxes with
IAU 2006-adjusted nutation. The primary independent comparator states that
expression explicitly: ERFA gmst06 + ee00(obl06,nut06a.dpsi). A separate gst06a
reference evaluates the IAU 2006 equation-of-origins expression.

On the current 1896 July 14 UT1 grid, the ERFA formulations differ by at most
2.5490720645393594e-13 radians. The maximum altitude and wrapped-azimuth
residuals against gst06a are respectively 1.2065015653206501e-11 and
4.75210981676355e-11 degrees. Both pass the retained 3e-11 and 1e-10 degree
criteria on this day. This is recorded explicitly in viewing-summary.json.
No tolerance has been changed and no standards-exact GAST claim is inferred.

The direct BPN frame rotation agrees independently with pnm06a to below
6e-14 degrees. Raw GMST, GAST, nutation and obliquity values are retained in
sidereal-diagnostics.csv. The library is unchanged. These implementation
comparisons are distinct from physical historical-time uncertainty.
