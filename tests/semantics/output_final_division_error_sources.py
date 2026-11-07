#!/usr/bin/env python3
"""FINAL string conversion retains a genuine scalar division-by-zero error."""
from pathlib import Path
import function_scope as scope

DIVISION = b"""<?php
declare(strict_types=0);
echo 'P';
class T {
    function __toString() {
        return 1 / 0;
    }
}
function h($b,$p) { return new T; }
ob_start('h'); echo 'A';
"""

CASES = {'native-division-error': DIVISION,
         'native-division-normal': DIVISION.replace(b'1 / 0', b'1 / 1')}
CATCH = DIVISION.replace(b'        return 1 / 0;',
                         b"        try { return 1 / 0; } catch (DivisionByZeroError) { return 'H'; }")
OVERRIDE = DIVISION.replace(b'        return 1 / 0;',
                            b"        try { return 1 / 0; } finally { return 'H'; }")
CLEANUP = DIVISION.replace(b'class T {', b'class D { function __destruct() { echo $missing; } }\nclass T {').replace(
    b'        return 1 / 0;', b'        $d = new D;\n        return 1 / 0;')

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-division-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
