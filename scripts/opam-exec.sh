#!/usr/bin/env bash
set -euo pipefail
project_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
exec opam exec --root="$project_dir/.tools/opam" --switch=5.1.0 -- \
  env OCAMLPATH="$project_dir/.tools/spectec/lib" "$@"
