#!/usr/bin/env python3
"""Fresh Exception factory results survive ordinary return cleanup before throw."""
from pathlib import Path
import function_scope as scope

CASES = {
    'factory-result': b"""<?php
echo 'P';
class T {
    function __toString() {
        $keep = 'T';
        throw make();
    }
}
function make() {
    $message = 'E';
    return new Exception($message);
}
function h($b,$p) { return new T; }
ob_start('h'); echo 'A';
""",
    'factory-result-local-cleanup': b"""<?php
echo 'P';
class D {
    function __destruct() { echo $missing; }
}
class T {
    function __toString() {
        $keep = 'T';
        throw make();
    }
}
function make() {
    $d = new D;
    $message = 'E';
    return new Exception($message);
}
function h($b,$p) { return new T; }
ob_start('h'); echo 'A';
""",
}

# Stop the model-only override control before its later scalar THROW_VALUE.
OVERRIDE = CASES['factory-result'].replace(
    b'    return new Exception($message);',
    b"    try { return new Exception($message); } finally { return 'H'; }")

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-factory-return', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
