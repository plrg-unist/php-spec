#!/usr/bin/env python3
"""FINAL conversion retains a quiet power TypeError."""
from pathlib import Path
import function_scope as scope

INVALID = b"""<?php
declare(strict_types=0);
echo 'P';
class T {
    function __toString() {
        return 2 ** 'X';
    }
}
function h($b,$p) { return new T; }
ob_start('h'); echo 'A';
"""
NORMAL = INVALID.replace(b"2 ** 'X'", b"2 ** '3'")
CASES = {'native-power-type-error': INVALID,
         'native-power-numeric-string': NORMAL}
CATCH = INVALID.replace(b"        return 2 ** 'X';",
                        b"        try { return 2 ** 'X'; } catch (TypeError) { return 'H'; }")
OVERRIDE = INVALID.replace(b"        return 2 ** 'X';",
                           b"        try { return 2 ** 'X'; } finally { return 'H'; }")
CLEANUP = INVALID.replace(b'class T {', b'class D { function __destruct() { echo $missing; } }\nclass T {').replace(
    b"        return 2 ** 'X';", b"        $d = new D;\n        return 2 ** 'X';")

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-power-type-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
