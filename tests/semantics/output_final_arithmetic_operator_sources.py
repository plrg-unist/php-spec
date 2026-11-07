#!/usr/bin/env python3
"""FINAL conversion retains quiet subtraction and multiplication TypeErrors."""
from pathlib import Path
import function_scope as scope

SUBTRACT = b"""<?php
declare(strict_types=0);
echo 'P';
class T {
    function __toString() {
        return 1 - 'X';
    }
}
function h($b,$p) { return new T; }
ob_start('h'); echo 'A';
"""
MULTIPLY = SUBTRACT.replace(b"1 - 'X'", b"1 * 'X'")
NORMAL = SUBTRACT.replace(b"1 - 'X'", b"1 - '2'")
CASES = {'native-subtract-type-error': SUBTRACT,
         'native-multiply-type-error': MULTIPLY,
         'native-subtract-numeric-string': NORMAL}
CATCH = SUBTRACT.replace(b"        return 1 - 'X';",
                         b"        try { return 1 - 'X'; } catch (TypeError) { return 'H'; }")
OVERRIDE = SUBTRACT.replace(b"        return 1 - 'X';",
                            b"        try { return 1 - 'X'; } finally { return 'H'; }")
CLEANUP = SUBTRACT.replace(b'class T {', b'class D { function __destruct() { echo $missing; } }\nclass T {').replace(
    b"        return 1 - 'X';", b"        $d = new D;\n        return 1 - 'X';")

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-arithmetic-operators', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
