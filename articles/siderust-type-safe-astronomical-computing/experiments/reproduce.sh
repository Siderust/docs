#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")" && pwd)
mode=applications
case "${1:-}" in
    --verify) exec python3 "$root/results/verify.py" ;;
    --full|--all) mode=full; shift ;;
    --tables) mode=tables; shift ;;
    --applications) shift ;;
    --help|-h)
        echo 'Usage: bash experiments/reproduce.sh [--applications|--full|--all|--tables] RUN_ID [KERNEL_DIRECTORY]'
        echo '       bash experiments/reproduce.sh --verify'
        exit 0 ;;
esac
run_id=${1:-$mode-$(date -u +%Y%m%dT%H%M%SZ)}
if [[ $# -gt 0 ]]; then shift; fi
exec python3 "$root/results/reproduce.py" --mode "$mode" "$run_id" "$@"
