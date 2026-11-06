#!/usr/bin/env python3
"""Fresh factory results thrown from an ordinary helper's private CV."""
from pathlib import Path
import function_scope as scope

CASES = {
    'helper-cv': b"""<?php
echo 'P';
class T {
    function __toString() {
        $keep = 'T';
        return fail();
    }
}
function fail() {
    $e = make();
    throw $e;
}
function make() { return new Exception('E'); }
function h($b,$p) { return new T; }
ob_start('h'); echo 'A';
""",
}

SIBLING = CASES['helper-cv'].replace(
    b"        $keep = 'T';\n        return fail();",
    b'        $e = make();\n        try { fail(); } catch (Exception $caught) {}\n        throw $e;')
REBIND = CASES['helper-cv'].replace(
    b"        $keep = 'T';", b'        $e = make();').replace(
    b'    throw $e;', b"    $e = 'H';\n    return 'H';")
CATCH = CASES['helper-cv'].replace(
    b'    throw $e;', b"    try { throw $e; } catch (Exception $caught) {}\n    return 'H';")
OVERRIDE = CASES['helper-cv'].replace(
    b'    throw $e;', b"    try { throw $e; } finally { return 'H'; }")
CLEANUP = CASES['helper-cv'].replace(
    b'class T {', b'class D { function __destruct() { echo $missing; } }\nclass T {').replace(
    b'    $e = make();', b'    $e = make();\n    $d = new D;')
RECIPIENT_BYREF = CASES['helper-cv'].replace(b'function fail()', b'function &fail()')
RECURSIVE = CASES['helper-cv'].replace(
    b'function fail() {\n    $e = make();',
    b'function fail() {\n    global $level;\n    $e = make();\n    if ($level--) { try { fail(); } catch (Exception $caught) {} }').replace(
    b'function h($b,$p) { return new T; }',
    b'function h($b,$p) { global $level; $level = 1; return new T; }')

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-factory-helper-cv', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
