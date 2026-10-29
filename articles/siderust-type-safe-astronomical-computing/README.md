# Siderust: Type-Safe Astronomical Computing in Rust

LaTeX source of a scientific article prepared for *Astronomy and Computing*.
It describes the Siderust architecture, type-safe astronomical interfaces,
independent reference comparisons, and terrestrial/lunar observing applications
using published **Siderust v0.16.0**.

## Files

- [`tex/main.tex`](tex/main.tex): complete manuscript; chapters, bibliography, figures and publication tables are below `tex/`.
- [`examples/`](examples/): self-contained Rust examples corresponding to the source listings in the article.
- [`submission/highlights.txt`](submission/highlights.txt): optional journal highlights.

Numerical tables and figure coordinates are preserved as presented in the
manuscript. The underlying v0.16.0 raw measurements, reference fixtures,
source provenance and independent reproduction package are stored in a separate
[supplement staging branch](https://github.com/VPRamon/siderust-paper/tree/supplement/siderust-v016-reproduction)
at immutable commit `bf8f3aec0ad50f4f3c01b26df64b6d78218bf66d`.
They are not part of the manuscript-source tree or its CI checks. The repository
remains private; no public data deposit or external dataset DOI is claimed.

## Checks

Requires Docker with TeX Live (the image is fixed in the Makefile), GNU Make,
Rust/Cargo **1.93.1** and an internet connection for initial crate downloads.

```sh
make pdf        # compile tex/main.pdf
make lint       # chktex
make examples   # cargo check --locked on all examples
make check      # PDF, LaTeX lint and Rust compilation
```

You can also invoke these commands from the repository root with
`make ARTICLE=siderust-type-safe-astronomical-computing <target>`.

## Try the examples

From `articles/siderust-type-safe-astronomical-computing/`:

```sh
cargo run --locked --manifest-path examples/Cargo.toml --bin qtty
cargo run --locked --manifest-path examples/Cargo.toml --bin tempoch
cargo run --locked --manifest-path examples/Cargo.toml --bin observe -- 2025-01-01T22:00:00Z 1.5 42.0
cargo run --locked --manifest-path examples/Cargo.toml --bin frame_repair
```

The geometric terrestrial observation prescribes DUT1 = 0 and omits refraction,
polar motion and apparent-place corrections. To evaluate the finite-distance
lunar observation or the runtime ephemeris example, supply a compatible
JPL/NAIF BSP kernel, such as the separately obtained DE440s:

```sh
cargo run --locked --manifest-path examples/Cargo.toml --bin earth_from_moon -- /path/to/de440s.bsp
cargo run --locked --manifest-path examples/Cargo.toml --bin runtime_ephemeris -- /path/to/de440s.bsp
```

The lunar example uses the analytical IAU_MOON orientation and geometric
altitude/azimuth. It is not terrain- or apparent-place corrected.

See [Siderust](https://github.com/Siderust/siderust) for the software source
and [its versioned Rust API](https://docs.rs/siderust/0.16.0/siderust/).
