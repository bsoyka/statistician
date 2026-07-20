#!/usr/bin/env bash
# Build Lambda deployment packages.
#
# Each package is assembled under build/<func>/ by copying the function's
# handler.py and the shared common/ directory.
#
# Usage:
#   scripts/build_lambdas.sh [func ...]
#
# If no arguments are given, all functions are built.
# Paths are resolved relative to the repository root regardless of the
# working directory from which the script is invoked.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

ALL_FUNCS=(
  public_stats
  public_facts
  private_stats
  private_volunteer
  private_ctl
  recompute_stats
)

if [[ $# -gt 0 ]]; then
  FUNCS=("$@")
else
  FUNCS=("${ALL_FUNCS[@]}")
fi

for func in "${FUNCS[@]}"; do
  src="$REPO_ROOT/funcs/$func/handler.py"
  if [[ ! -f "$src" ]]; then
    echo "Error: no handler found for '$func' (expected $src)" >&2
    exit 1
  fi

  dest="$REPO_ROOT/build/$func"
  rm -rf "$dest"
  mkdir -p "$dest"
  cp "$src" "$dest/handler.py"
  cp -R "$REPO_ROOT/funcs/common" "$dest/common"
  echo "Built $func"
done
