#!/usr/bin/env bash
set -euo pipefail
project_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$project_dir"
read -r -a includes <<< "$(.tools/php/bin/php-config --includes)"
cc -std=c11 -O2 -Wall -Wextra -Wno-unused-parameter -shared -fPIC \
  "${includes[@]}" native/php_file.c -o .tools/php-file.so
.tools/php/bin/php -n -d "extension=$project_dir/.tools/php-file.so" \
  -r 'if (!function_exists("php_spec_parse_file") || !function_exists("php_spec_lex_file") || !function_exists("php_spec_encoding_name")) exit(1); echo "PHP file scanner helper ready\n";'
