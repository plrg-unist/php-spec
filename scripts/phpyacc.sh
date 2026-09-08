#!/usr/bin/env bash
set -euo pipefail
project_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
exec "$project_dir/.tools/php/bin/php" -n -d "error_reporting=E_ALL & ~E_DEPRECATED" "$project_dir/scripts/phpyacc.php" "$@"
