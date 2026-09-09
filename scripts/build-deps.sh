#!/usr/bin/env bash
# All non-system inputs are vendored. This script never updates repositories.
set -euo pipefail
project_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$project_dir"
jobs=${JOBS:-8}
phase=${1:-all}
mkdir -p .tools
if [[ "$phase" == all || "$phase" == php ]]; then
  if [[ ! -x .tools/php/bin/php ]]; then
    mkdir -p .tools/php-build
    if [[ ! -d .tools/php-src ]]; then cp -a vendor/php-src .tools/php-src; fi
    (
      cd .tools/php-build
      ../php-src/configure --prefix="$project_dir/.tools/php" \
        --disable-all --enable-cli --disable-cgi --disable-phpdbg \
        --without-pear --enable-tokenizer --enable-mbstring --disable-mbregex --enable-ctype
      make -j"$jobs"
      make install
    )
  fi
  .tools/php/bin/php -n -r '
    if (PHP_VERSION !== "8.5.10" || PHP_SAPI !== "cli" ||
        !extension_loaded("tokenizer") || !extension_loaded("json") ||
        !extension_loaded("mbstring") || !extension_loaded("ctype")) exit(1);
    echo "PHP ", PHP_VERSION, " CLI; tokenizer/JSON/mbstring/ctype enabled\n";'
  scripts/build-file-helper.sh
  scripts/build-request-provider.sh
fi
if [[ "$phase" == all || "$phase" == opam ]]; then
  opam_root="$project_dir/.tools/opam"
  if [[ ! -f "$opam_root/config" ]]; then
    opam init --bare --disable-sandboxing --no-setup --root="$opam_root" \
      local "$project_dir/vendor/opam-repository" -y
    cp -a vendor/opam-cache "$opam_root/download-cache"
  fi
  if ! opam switch list --root="$opam_root" --short | awk '$0 == "5.1.0" {found=1} END {exit !found}'; then
    opam switch create --root="$opam_root" 5.1.0 ocaml-base-compiler.5.1.0 --jobs="$jobs" -y
  fi
  mapfile -t packages < dependencies/opam-packages.txt
  opam install --root="$opam_root" --switch=5.1.0 --jobs="$jobs" -y "${packages[@]}"
fi
if [[ "$phase" == all || "$phase" == spectec ]]; then
  scripts/opam-exec.sh dune build --root vendor/p4-spectec \
    --build-dir "$project_dir/.tools/spectec-build" --profile=release \
    p4spec/bin/main.exe p4spec/bin/boot.exe @install
  scripts/opam-exec.sh dune install --root vendor/p4-spectec \
    --build-dir "$project_dir/.tools/spectec-build" \
    --prefix "$project_dir/.tools/spectec" --sections=lib,bin p4spectec
fi
case "$phase" in all|php|opam|spectec) ;; *) echo 'usage: build-deps.sh [all|php|opam|spectec]' >&2; exit 2;; esac
