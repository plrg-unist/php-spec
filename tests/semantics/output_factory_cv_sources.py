#!/usr/bin/env python3
"""Fresh factory results retain provenance through ordinary native CV storage."""
from pathlib import Path
import function_scope as scope

CASES = {
    'factory-cv': b"""<?php
echo 'P';
class T {
    function __toString() {
        $e = make();
        throw $e;
    }
}
function make() {
    $message = 'E';
    return new Exception($message);
}
function h($b,$p) { return new T; }
ob_start('h'); echo 'A';
""",
    'factory-two-cvs': b"""<?php
echo 'P';
class T {
    function __toString() {
        $first = bridge();
        $later = bridge();
        throw $first;
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
}

MINIMAL_TWO = b"""<?php
echo 'P';
class T {
    function __toString() {
        $first = make();
        $later = make();
        throw $first;
    }
}
function make() { return new Exception('E'); }
function h($b,$p) { return new T; }
ob_start('h'); echo 'A';
"""

# Model-only controls preserve the ordinary factory/constructor domains.
CLEANUP = CASES['factory-cv'].replace(
    b'class T {', b'class D { function __destruct() { echo $missing; } }\nclass T {').replace(
    b'        $e = make();', b'        $e = make();\n        $d = new D;')
REBIND = CASES['factory-cv'].replace(
    b'        throw $e;', b"        $e = 'H';\n        throw $e;")
CATCH = CASES['factory-two-cvs'].replace(
    b'        throw $first;',
    b'        try { throw $first; } catch (Exception $caught) {}\n        throw $later;')

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-factory-cv', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
