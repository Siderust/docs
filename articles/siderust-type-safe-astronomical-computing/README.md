# Siderust: Type-Safe Astronomical Computing in Rust

Scientific article prepared for *Astronomy and Computing*, evaluating
**Siderust v0.18.1** and **Tempoch v0.11.2**. No acceptance status or DOI is asserted.
The manuscript and reproducibility materials are available at
[github.com/Siderust/docs](https://github.com/Siderust/docs).

- [LaTeX sources](tex/main.tex), with chapters, bibliography, figures and tables in `tex/`.
- [Executable Rust examples](examples/README.md), included directly as manuscript listings.
- [Scientific reproduction](experiments/README.md), including independent references,
  original inputs, acceptance criteria, recorded results and SHA-256 manifests.
- [Journal highlights](submission/highlights.txt).

## Build and source checks

Requires Docker, GNU Make, Python 3, `uv` and Rust/Cargo **1.93.1** (pinned by
`rust-toolchain.toml`). Initial runs download public dependencies. The Makefile
uses TeX Live 2025 historic, including `latexindent` 3.24.7 and ChkTeX 1.7.9.

From this directory:

```sh
make pdf          # tex/build/main.pdf
make fmt          # format hand-edited LaTeX using .latexindent.yaml
make fmt-check    # compare formatting without modifying sources; check hygiene
make lint         # ChkTeX diagnostics; nonzero on enabled warnings
make examples     # cargo check --locked on all examples
make integrity    # scientific source/input/output SHA-256 verification
make tables-check # regenerate publication tables, macros and data figure
make check        # all checks above, except the modifying fmt command
```

Fix formatting failures with `make fmt`, then rerun `make fmt-check`.
The formatter uses four-space indentation and 100-column prose wrapping where
practical; equations, tables, listings and long commands may exceed that width.
`generated-tex.txt` lists generated sources: change their generators or scientific
inputs as appropriate, then regenerate them rather than running a formatter on them.
`fmt-check` also rejects trailing whitespace, CRLF, missing final newlines and
conflict markers in every TeX source. ChkTeX follows the established policy:
warnings 2, 8, 13, 18 and 24 are disabled (spacing, dash/quote and layout heuristics);
all other diagnostics fail the check.

Commands also work from the repository root with
`make ARTICLE=siderust-type-safe-astronomical-computing <target>`.
CI discovers articles automatically, checks source formatting, compiles PDFs,
runs LaTeX diagnostics, compiles locked examples, verifies scientific integrity
and checks generated outputs. Each article PDF is uploaded as a CI artifact.
The full scientific suite is available locally as described below.

## Reproduce

```sh
bash experiments/reproduce.sh --verify
bash experiments/reproduce.sh --tables tables-001
bash experiments/reproduce.sh applications-001
bash experiments/reproduce.sh --full full-001
```

The full mode runs ERFA time/frame comparisons, CSPICE/SPK and analytical
positions, Antares observing windows, Earth-from-Moon finite-distance parallax,
lunar/Martian surfaces, boundaries, compiler/runtime controls and upstream
EOP/frame/SPK regressions. Outputs go to a new `experiments/runs/<id>/` directory.
The [reproduction guide](experiments/README.md) documents dependencies, kernel
retrieval, reference implementations and exact comparison policies.

Antares uses 1896 July 14 UT1 with a prescribed historical Delta T model;
the lunar observation uses 2017 October 1 at 17:14 TT. Numerical agreement is
conditional on the documented models and is distinct from physical accuracy.
