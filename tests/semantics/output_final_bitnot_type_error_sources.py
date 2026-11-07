#!/usr/bin/env python3
"""FINAL conversion retains quiet bool/null bitwise-not TypeErrors."""
from pathlib import Path
import function_scope as scope

TRUE = b"""<?php
declare(strict_types=0);
echo 'P';
class T {
    function __toString() {
        return ~true;
    }
}
function h($b,$p) { return new T; }
ob_start('h'); echo 'A';
"""
FALSE = TRUE.replace(b'~true', b'~false')
NULL = TRUE.replace(b'~true', b'~null')
NORMAL_INT = TRUE.replace(b'~true', b'~2')
NORMAL_STRING = TRUE.replace(b'~true', b"~'X'")
CASES = {'native-bitnot-true-type-error': TRUE,
         'native-bitnot-false-type-error': FALSE,
         'native-bitnot-null-type-error': NULL,
         'native-bitnot-integer': NORMAL_INT,
         'native-bitnot-string': NORMAL_STRING}
CATCH = TRUE.replace(b'        return ~true;',
                     b"        try { return ~true; } catch (TypeError) { return 'H'; }")
OVERRIDE = TRUE.replace(b'        return ~true;',
                        b"        try { return ~true; } finally { return 'H'; }")
CLEANUP = TRUE.replace(b'class T {', b'class D { function __destruct() { echo $missing; } }\nclass T {').replace(
    b'        return ~true;', b'        $d = new D;\n        return ~true;')

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-bitnot-type-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
