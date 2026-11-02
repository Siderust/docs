# Provenance and terms

The numerical runners, compiler fixtures and independent references accompany
the manuscript. `SOURCE-MANIFEST.json` records retained scientific identities
and the original identities of references adapted for portable input paths.
Reproduction automation is MIT-licensed (`LICENSE`); manuscript, figures and
author code retain the repository's applicable license terms.

The full Siderust and Tempoch source trees are **not** redistributed here.
`manifests/upstream.json` identifies public immutable Git revisions, producer URLs,
archive hashes and every file hash in the original exports. Full replay downloads
those unmodified trees into its new run and retains their AGPL-3.0-only license
files and notices. The complete AGPL text is also in `licenses/AGPL-3.0-only.txt`.
Locked third-party Rust and Python dependencies are obtained from crates.io and
public PyPI; their software and binaries are not relicensed by this artifact.

The unmodified scientific kernels are fetched from NASA/JPL/NAIF using
`../lunar/inputs.json`: JPL DE440s, NAIF `naif0012.tls` and `pck00011.tpc`.
Their headers and embedded notices remain intact. They are not bundled in the
publication repository or relicensed under MIT or CC BY. Consult the producer's
[NAIF rules](https://naif.jpl.nasa.gov/naif/rules.html) for use/redistribution.
No standalone SPICE toolkit or Python environment is included in the repository.

The UTC–TAI snapshot is supplied through locked `siderust-archive` 0.1.5;
`recorded/time_data.provenance.toml` preserves its producer/source checksums.
No measured IERS dataset is used by the independent comparisons. Native EOP
regressions use synthetic inputs.
