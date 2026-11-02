# Siderust scientific articles

Manuscripts and reproducibility materials for the
[Siderust](https://github.com/Siderust) astronomical software ecosystem.

| Article | Sources and instructions |
| --- | --- |
| Siderust: Type-Safe Astronomical Computing in Rust | [Article directory](articles/siderust-type-safe-astronomical-computing/README.md) |

The current article is prepared for *Astronomy and Computing* and evaluates
**Siderust v0.18.1** and **Tempoch v0.11.2**. Its LaTeX, bibliography, figures,
executable examples, scientific inputs and independent reference implementations
are provided together. No acceptance status, publication date or DOI is asserted.

## Build and validate

Requires Docker, GNU Make, Python 3, `uv` and the article's pinned Rust toolchain.

```sh
make pdf         # compile the selected article
make fmt         # correct hand-edited LaTeX formatting
make fmt-check   # non-modifying formatting and hygiene check
make lint        # ChkTeX diagnostics
make examples    # compile examples with locked dependencies
make check       # all checks, including integrity and generated publication outputs
make pdf-all     # compile all discovered articles
make check-all   # check all discovered articles
```

Select an article with `ARTICLE=<slug>`; the current article is the default.
See its [reproduction guide](articles/siderust-type-safe-astronomical-computing/experiments/README.md)
for table generation and the complete scientific experiments.

## Add an article

Create `articles/<slug>/README.md`, `Makefile` and `tex/main.tex`.
Provide `pdf`, `fmt`, `fmt-check`, `lint`, `examples` and `check` targets, following
the existing article's conventions; `examples` may be a no-op when none exist.
Use `generated-tex.txt` to identify generated TeX excluded from independent formatting.

`scripts/discover-articles.py` validates every article directory and emits the
GitHub Actions matrix. Pull requests and pushes to `main` run each article's
checks independently and upload its `tex/build/main.pdf`. Adding an article
requires no workflow edits. CI never publishes or modifies the repository.
