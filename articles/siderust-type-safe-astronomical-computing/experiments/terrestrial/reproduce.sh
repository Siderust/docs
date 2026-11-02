#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
set -euo pipefail
experiment_root=$(cd -- "$(dirname -- "$0")" && pwd)
article_root=$(cd -- "$experiment_root/../.." && pwd)
run_id=${1:-replay-$(date -u +%Y%m%dT%H%M%SZ)}
[[ "$run_id" =~ ^[a-zA-Z0-9_-]+$ ]] || { echo 'Invalid run id' >&2; exit 2; }
run_root="$experiment_root/runs/$run_id"
[[ ! -e "$run_root" ]] || { echo "Refusing to overwrite $run_root" >&2; exit 2; }
cd "$article_root"
sha256sum --check "$experiment_root/SHA256SUMS"
mkdir -p "$run_root"
# Isolate the build and reference environment from the author's workspace.
export CARGO_TARGET_DIR="$run_root/target"
unset RUSTFLAGS CARGO_ENCODED_RUSTFLAGS CARGO_BUILD_TARGET
uv venv --python 3.12.13 "$run_root/pyenv"
uv pip install --python "$run_root/pyenv/bin/python" -r "$experiment_root/requirements.txt"
py="$run_root/pyenv/bin/python"
cargo +1.93.1 -V > "$run_root/cargo-version.txt"
rustc +1.93.1 -Vv > "$run_root/rustc.txt"
"$py" -VV > "$run_root/python-version.txt"
cargo +1.93.1 tree --locked --manifest-path examples/Cargo.toml > "$run_root/cargo-tree.txt"
# Validate representative orientations before generating the full daily grid.
cargo +1.93.1 run --locked --manifest-path examples/Cargo.toml --bin viewing -- "$run_root/representative" --representative
"$py" scripts/validate_antares.py --data "$run_root/representative" --catalog "$experiment_root/catalog.json" --representative > "$run_root/representative.log"
cargo +1.93.1 run --locked --manifest-path examples/Cargo.toml --bin viewing -- "$run_root"
cargo +1.93.1 run --locked --quiet --manifest-path examples/Cargo.toml --bin viewing_events -- "$run_root"
cargo +1.93.1 run --locked --quiet --manifest-path examples/Cargo.toml --bin historical_feasibility > "$run_root/historical-feasibility.csv"
cargo +1.93.1 run --locked --quiet --manifest-path examples/Cargo.toml --bin antares_diagnostics > "$run_root/sidereal-diagnostics.csv"
"$py" scripts/validate_antares.py --data "$run_root" --catalog "$experiment_root/catalog.json" > "$run_root/reference.log"
mkdir -p "$run_root/generated/tex/tables"
cp tex/tables/release-values.tex tex/tables/release-validation.tex "$run_root/generated/tex/tables/"
python3 scripts/generate_antares_macros.py --article "$run_root/generated" --summary "$run_root/viewing-summary.json"
python3 scripts/generate_figures.py --article "$run_root/generated" --data "$run_root/viewing.csv"
python3 scripts/verify_antares_figure.py --figure "$run_root/generated/tex/figures/observing-window.tex" --data "$run_root/viewing.csv"
# Deterministic evidence comparison, not an expected-result oracle for ERFA.
for name in viewing.csv viewing-epochs.csv viewing-selected.csv viewing-spans.csv viewing-brackets.csv viewing-events.csv historical-feasibility.csv; do
    cmp "$run_root/$name" "$experiment_root/recorded/$name"
done
sha256sum --check "$experiment_root/SHA256SUMS"
printf 'Antares replay passed: %s\n' "$run_root"
