#!/usr/bin/env python3
"""Implicit string return checking during native FINAL object conversion."""
from pathlib import Path
import function_scope as scope

STRICT = b"""<?php
declare(strict_types=1);
echo 'P';
class T {
    function __toString() {
        $keep = 'T';
        return 42;
    }
}
function h($b,$p) { return new T; }
ob_start('h'); echo 'A';
"""

CASES = {
    'strict-return-error': STRICT,
    'weak-return-coercion': STRICT.replace(b'strict_types=1', b'strict_types=0'),
}

CATCH = STRICT.replace(b'        return 42;',
                       b"        try { return 42; } catch (TypeError $caught) { return 'H'; }")
OVERRIDE = STRICT.replace(b'        return 42;',
                          b"        try { return 42; } finally { return 'H'; }")
CLEANUP = STRICT.replace(b'class T {',
                         b'class D { function __destruct() { echo $missing; } }\nclass T {').replace(
    b"        $keep = 'T';", b"        $keep = 'T';\n        $d = new D;")

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-return-type', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
