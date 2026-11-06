#!/usr/bin/env python3
"""Fresh by-value factory results cross real ordinary return-frame contours."""
from pathlib import Path
import function_scope as scope

CASES = {
    'factory-contour-bridge': b"""<?php
echo 'P';
class T {
    function __toString() {
        $keep = 'T';
        throw bridge();
    }
}
function bridge() {
    return make();
}
function make() {
    $message = 'E';
    return new Exception($message);
}
function h($b,$p) { return new T; }
ob_start('h'); echo 'A';
""",
    'factory-contour-recursive': b"""<?php
echo 'P';
class T {
    function __toString() {
        $keep = 'T';
        throw recur();
    }
}
function recur() {
    global $level;
    if ($level--) return recur();
    $message = 'R';
    return new Exception($message);
}
function h($b,$p) { global $level; $level = 2; return new T; }
ob_start('h'); echo 'A';
""",
}

# Model-only controls; the override stops before its later scalar THROW_VALUE.
CLEANUP = CASES['factory-contour-bridge'].replace(
    b'class T {', b'class D { function __destruct() { echo $missing; } }\nclass T {').replace(
    b'function bridge() {\n    return make();',
    b'function bridge() {\n    $d = new D;\n    return make();')
OVERRIDE = CASES['factory-contour-bridge'].replace(
    b'    return make();', b"    try { return make(); } finally { return 'H'; }")

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-factory-contour', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
