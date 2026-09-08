#!/usr/bin/env bash
set -euo pipefail
project_root=$(cd "$(dirname "$0")/.." && pwd)
work="$project_root/.tools/parser-regenerate"
mkdir -p "$work"
cp -a "$project_root/vendor/php-parser-source/grammar" "$work/"
patch --batch --directory="$work" -p1 < "$project_root/patches/php-parser-grammar.patch"
KMYACC="$project_root/scripts/phpyacc.sh" "$project_root/.tools/php/bin/php" -n "$work/grammar/rebuildParsers.php"
if [[ ${1:---check} == --write ]]; then
    cp "$work/lib/PhpParser/Parser/Php8.php" "$project_root/vendor/php-parser/lib/PhpParser/Parser/Php8.php"
else
    cmp "$work/lib/PhpParser/Parser/Php8.php" "$project_root/vendor/php-parser/lib/PhpParser/Parser/Php8.php"
fi
