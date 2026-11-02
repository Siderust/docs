# Reproduce the scientific results

Run these commands from `articles/siderust-type-safe-astronomical-computing/`.
The original observations, numerical populations, software and acceptance bounds
are fixed. Each execution creates `experiments/runs/RUN_ID/` and refuses to
reuse an existing identifier. Nothing in any `recorded/` directory is updated.

| Purpose | Command |
| --- | --- |
| Verify publication files and original evidence; no downloads | `bash experiments/reproduce.sh --verify` |
| Both featured applications | `bash experiments/reproduce.sh applications-001` |
| Entire numerical suite, both applications, semantic controls, upstream regressions, examples and table verification | `bash experiments/reproduce.sh --full full-001` |
| All supported scientific checks together | `bash experiments/reproduce.sh --all all-001` (alias of `--full`) |
| Regenerate all result tables, macros and the data figure from preserved evidence | `bash experiments/reproduce.sh --tables tables-001` |

`--applications RUN_ID` explicitly selects the default mode. Application/full
modes also accept a final kernel directory containing the three **unchanged**
inputs named below. Otherwise they download them into the new run. Tables mode
needs no kernels, Rust execution or upstream source downloads.

## Environment

The tested scientific environment is Linux x86-64, Rust/Cargo **1.93.1**, Python
**3.12.13**, PyERFA **2.0.1.5** / ERFA **2.0.1**, SpiceyPy **6.0.0** /
CSPICE **N0067**, and NumPy **2.5.4**. The script creates its own Python environment
and installs hash-pinned public distributions from `requirements.lock`.
It checks all these versions and that Python assertions are enabled.

For native execution install Bash, Python 3.9 or later for the launcher, `uv`,
Rustup with toolchain 1.93.1, a C compiler/linker, `pkg-config`, OpenSSL development
headers and CA certificates. `uv` 0.12.0 is used in the tested container.
Allow several GB of disk for independent Rust builds and initial internet access
to public PyPI, crates.io, GitHub, Python distributions and NAIF.
The three committed Cargo lockfiles select the same 92 registry packages,
including Siderust 0.18.1, Tempoch/Tempoch-core 0.11.2, qtty 0.8.6 and affn 0.12.1.
The original release build settings are retained for the numerical runner.

Alternatively, use the supplied isolated environment (Docker on Linux):

```bash
docker build -f experiments/results/Dockerfile -t siderust-paper-replay .
replay_scratch=$(mktemp -d)
docker run --rm --user "$(id -u):$(id -g)" \
  -v "$PWD:/paper" -v "$replay_scratch:/scratch" \
  siderust-paper-replay bash experiments/reproduce.sh --full docker-full-001
```

Only the article tree and a fresh scratch directory are mounted. The scratch
contains downloaded tool/dependency caches; the run and its report remain under
`experiments/runs/` in the article tree. This image is for scientific replay;
the manuscript's TeX build uses the separate Makefile environment.

## Public inputs and immutable evidence

`lunar/inputs.json` supplies producer URLs and SHA-256 values for DE440s,
`naif0012.tls` and `pck00011.tpc`. Every input is verified before execution.
Failed downloads cannot be accepted as valid kernels. The complete numerical
suite retrieves the original Siderust and Tempoch regression sources at exact
Git revisions in `results/manifests/upstream.json`, verifying both the archive
and every source file against the original exports. No upstream tree is vendored.
The source licenses and NAIF terms are explained in
[results/THIRD_PARTY.md](results/THIRD_PARTY.md).

Original evidence is in `terrestrial/recorded/`, `lunar/recorded/` and
`results/recorded/`. Scientific evidence/source identities are recorded in `results/SOURCE-MANIFEST.json`; the complete integrity
inventory is `results/manifest.json`. Check it either through `--verify` or:

```bash
sha256sum --check experiments/results/SHA256SUMS
```

Compiler rejection outcomes and expected error codes are in
`results/recorded/controls-summary.json`. Full reproduction also retains fresh
compiler diagnostic logs. Scientific source revisions and kernel identities are
in `results/manifests/original-provenance.json` and `upstream.json`.

## Experiments and publication outputs

Paths in this table are relative to `experiments/` except `tex/` and `scripts/`,
which are relative to the article. The machine-readable map is
`results/manifests/experiments.json`. Full mode executes every row.

| Manuscript evidence | Source and independent check | Inputs / original outputs | Generated publication source |
| --- | --- | --- | --- |
| Rotation/time agreement: 1,000 ERA, GMST, obliquity and BPN cases; 13 UTC labels, full-JD and split seconds | `results/runner/src/bin/validation.rs`; `results/reference/extended.py` (ERFA and Decimal) | `results/recorded/rotations*.csv`, `utc*.csv`; synthetic EOP regressions | `tex/tables/release-validation.tex`, `release-time.tex` |
| SPK and analytical positions: 1,000 Earth/Moon epochs | `results/runner/src/main.rs`; `results/reference/ephemeris.py` (CSPICE and ERFA `ecm06`) | DE440s; `ephemeris.csv`, `reference.csv`, four residual CSVs in `results/recorded/` | `release-validation.tex`, `release-models.tex` |
| Generic surfaces: 5 lunar matrices, 30 directions, 10 finite targets, 4 Mars cases | `validation.rs`; `extended.py` (IAU_MOON/CSPICE and analytical geometry) | `lunar-surface*.csv`, `mars.csv` | `release-surface.tex` |
| Analytical boundaries: 48 lunar + 32 Mars; the 12 vertical cases are a subset of 48 | Independent `extended.py --prepare`, then `validation.rs` and `extended.py` | `boundary-input.csv`, `boundary-reference.csv`, `boundaries.csv`; `extended-residuals.csv` | `results-values.tex` and Chapter 8 prose |
| Five static mismatches; runtime invalid/degenerate/mismatched geometry | `results/controls/src/bin/`, `results/check_controls.py`, `runtime_controls.rs` | `controls-summary.json`, `runtime-controls.log` | `results-values.tex` and semantic-contract prose |
| Converted TT coverage probes and upstream native regressions | `coverage.rs`; exact public upstream tests | `coverage.log`; `eop-tests.log` (10), `frame-tests.log` (11), `spk-surface-tests.log` (36+11) | Chapter 8 coverage/semantic prose |
| Historical Antares, 289 samples and refined events | Public examples; `scripts/validate_antares.py` (ERFA) | `terrestrial/catalog.json`, all terrestrial CSV/JSON records | Antares rows, `release-values.tex`, `tex/figures/observing-window.tex` |
| Finite Earth-from-Moon observation | Public examples; `scripts/validate_lunar_application.py` (CSPICE) | `lunar/inputs.json`, lunar CSV/JSON/text records | `release-values.tex` |

The canonical table generator is `scripts/generate_results_tables.py`.
`results/regenerate.py` additionally derives the display ceilings from preserved
maxima, initializes the macro layout without copying existing numerical TeX,
runs the application generators, verifies all figure points/insets and compares
all TeX outputs listed in `../generated-tex.txt` byte-for-byte with publication sources.

## What a successful replay means

A full run starts with empty numerical output. Rust calculates each population;
independent references calculate expected values from the prescribed scientific
inputs and apply the **original** bounds before any comparison with the preserved
records. No original numerical output is seeded into this calculation. All deterministic CSV/text outputs
must then match the originals byte-for-byte; summaries must match as parsed JSON.
The sole CSV exception is `extended-residuals.csv`: the retained original and its
authoritative producer order the observable groups differently and use LF/CRLF.
All 4,815 residuals must match as **exact fields**, keyed by `(observable, case)`,
with identical headers/case populations and no duplicate keys. No numerical
tolerance or rounding is introduced by this semantic comparison.
Regression test populations and expected compiler diagnostics are checked too.

Outputs are `data/` (fresh scientific results), `logs/` (builds/references/tests),
`sources/` (verified public upstream source downloads), `kernels/`, `generated/`,
`environment.json`, `bootstrap-commands.json`, `commands.json`, `evidence-comparison.json`, `verification.json`
and `report.json`. The top-level report says `passed` only after every required
step and the final integrity check succeeds. Any missing input, checksum mismatch,
wrong environment, compiler-control anomaly, numerical-bound violation or output
difference exits nonzero. Partial failed runs are retained for diagnosis; use a
new identifier to retry. Strict byte identity may expose platform/libm differences;
it does not authorize changing the numerical bounds or replacing original records.

In applications mode only the two applications are recalculated; original core
summaries are used solely for table formatting and explicitly identified in the
report. Tables mode uses only preserved evidence. Timing-dependent original test
logs and environment metadata are not required to match a new machine.

Scientific conventions remain explicit: the SPK/analytical comparisons use the
canonical IAU 2006 mean-ecliptic J2000 normalization, not SPICE ECLIPJ2000;
analytical-theory differences are distinct from same-model implementation error.
Converted TT endpoint probes are distinct from inclusive native TDB bounds.
The zero-azimuth convention is retained at vertical lunar directions.

The [Antares notes](terrestrial/README.md), [lunar notes](lunar/README.md) and
[time-model notes](TIME_MODELS.md) explain UT1, Delta T, matched TT-to-TDB,
finite-distance geometry and physical limitations. Numerical agreement does not
validate historical Delta T, catalog motion, terrain or orientation accuracy.
