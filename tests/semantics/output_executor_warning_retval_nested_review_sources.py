#!/usr/bin/env python3
"""Normal Warning retval cleanup receives nested named and callable starts."""
from pathlib import Path

import function_scope as scope
from output_executor_invalid_sources import ORIGINALS as INVALID


BASE = INVALID['warning-return-object']
OLD = b'''class WarningReturnOB11 { function __destruct() { echo "R|"; } }
set_error_handler(static function ($level, $message) { echo "H:", $level, "|"; return new WarningReturnOB11; });'''
assert BASE.count(OLD) == 1

ORIGINALS = {}
for name, prefix, call in (
    ('named-unpacked-null', b'',
     b'ob_start(...["flags" => 3, "chunk_size" => 1, "callback" => null])'),
    ('temporary-pure-callable', b'''class NestedCallableOB14 {
    public function __invoke($a, $b, $c, $d) { echo "BAD_INVOKE|"; }
    public function __destruct() { echo "NK|"; }
}
''', b'ob_start(new NestedCallableOB14)'),
):
    replacement = prefix + b'''class WarningReturnOB14 {
    public function __destruct() { echo "R1|"; echo ''' + call + b''' ? "RT|" : "RF|"; echo "R2|"; }
}
set_error_handler(static function ($level, $message) {
    echo "H:", $level, "|";
    if ($level === 2) { return new WarningReturnOB14; }
    return true;
});'''
    ORIGINALS[name] = BASE.replace(OLD, replacement)


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(ORIGINALS, 'output-executor-warning-retval-nested-review',
                                    Path(__file__), publish=False, model_seconds=180) else 1)
