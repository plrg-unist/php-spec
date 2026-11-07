#!/usr/bin/env python3
"""FINAL return checks resolve a defined ordinary compiled scalar CV."""
from pathlib import Path
import function_scope as scope

STRICT = b"""<?php
declare(strict_types=1);
echo 'P';
class T {
    function __toString() {
        $r = 42;
        return $r;
    }
}
function h($b,$p) { return new T; }
ob_start('h'); echo 'A';
"""

CASES = {'native-cv-strict': STRICT,
         'native-cv-weak': STRICT.replace(b'strict_types=1', b'strict_types=0')}
CATCH = STRICT.replace(b'        return $r;',
                       b"        try { return $r; } catch (TypeError) { return 'H'; }")
OVERRIDE = STRICT.replace(b'        return $r;',
                          b"        try { return $r; } finally { return 'H'; }")
CLEANUP = STRICT.replace(b'class T {', b'class D { function __destruct() { echo $missing; } }\nclass T {').replace(
    b'        return $r;', b'        $d = new D;\n        return $r;')

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-cv-return-type', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
