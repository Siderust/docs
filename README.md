# Siderust articles

Scientific articles and publication sources for the [Siderust](https://github.com/Siderust) astronomical software ecosystem.

| Article | Source |
| --- | --- |
| **Siderust: Type-Safe Astronomical Computing in Rust** | [articles/siderust-type-safe-astronomical-computing/](articles/siderust-type-safe-astronomical-computing/README.md) |

Each article contains its manuscript, bibliography, figures and small executable examples. Internal reviews, scientific test runners and raw measurement datasets are not part of the publication sources. The Siderust v0.16.0 scientific reproduction material is preserved in a separate [supplement staging branch](https://github.com/VPRamon/siderust-paper/tree/supplement/siderust-v016-reproduction), pending an author-approved permanent public deposit.

## Build

```sh
make ARTICLE=siderust-type-safe-astronomical-computing pdf       # PDF via TeX Live/Docker
make ARTICLE=siderust-type-safe-astronomical-computing lint      # LaTeX grammar/style diagnostics
make ARTICLE=siderust-type-safe-astronomical-computing examples  # Compile Rust examples
make ARTICLE=siderust-type-safe-astronomical-computing check     # All three checks
```

Run `make pdf`, `make lint`, `make examples` or `make check` directly inside `articles/siderust-type-safe-astronomical-computing/`.

## Add an article

Create `articles/<slug>/` with its `README.md`, `Makefile`, and `tex/main.tex`. Provide `pdf`, `lint`, `examples` and `check` targets; use a no-op `examples` target if the article has none. GitHub Actions discovers article folders and produces separate PDFs.

The article repository currently is private. It does not claim a publicly deposited raw dataset, journal acceptance or a DOI.
