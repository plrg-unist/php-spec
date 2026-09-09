#!/usr/bin/env bash
set -euo pipefail
project_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$project_dir"
mkdir -p .tools
cc -std=c11 -Wall -Wextra -Werror -shared -fPIC \
  native/request_clock.c -o .tools/request-clock.so
