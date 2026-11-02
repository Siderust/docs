# Numerical validation

See the canonical [reproduction guide](../README.md) for commands, prerequisites,
scientific conventions and the experiment-to-publication map.

- `runner/`: Rust numerical experiments and runtime controls.
- `controls/`: five expected compile-time semantic failures.
- `reference/`: independent ERFA/CSPICE and analytical reference implementations.
- `recorded/`: scientific outputs and reference residuals used by the publication.
- `manifests/experiments.json`: populations, sources, reference checks and outputs.
- `manifests/original-provenance.json`: software, kernel and observation provenance.
- `manifests/upstream.json`: immutable upstream regression sources and hashes.
- `manifests/publication-layout.json`: result macro order and display rounding policy.
- `SOURCE-MANIFEST.json`: retained scientific evidence and implementation identities.
- `manifest.json` and `SHA256SUMS`: publication integrity inventory.

`reproduce.py` executes experiments, `regenerate.py` checks publication outputs,
and `verify.py` checks integrity without scientific Python dependencies.
Fresh outputs are written only below `../runs/`.
