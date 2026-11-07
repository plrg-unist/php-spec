#!/usr/bin/env python3
"""FINAL conversion retains quiet unary arithmetic TypeErrors."""
from pathlib import Path
import function_scope as scope

POSITIVE = b"""<?php
declare(strict_types=0);
echo 'P';
class T {
    function __toString() {
        return +'X';
    }
}
function h($b,$p) { return new T; }
ob_start('h'); echo 'A';
"""
NEGATIVE = POSITIVE.replace(b"+'X'", b"-'X'")
NORMAL = POSITIVE.replace(b"+'X'", b"+'2'")
CASES = {'native-unary-plus-type-error': POSITIVE,
         'native-unary-minus-type-error': NEGATIVE,
         'native-unary-plus-numeric-string': NORMAL}
CATCH = POSITIVE.replace(b"        return +'X';",
                         b"        try { return +'X'; } catch (TypeError) { return 'H'; }")
OVERRIDE = POSITIVE.replace(b"        return +'X';",
                            b"        try { return +'X'; } finally { return 'H'; }")
CLEANUP = POSITIVE.replace(b'class T {', b'class D { function __destruct() { echo $missing; } }\nclass T {').replace(
    b"        return +'X';", b"        $d = new D;\n        return +'X';")

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-unary-type-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
