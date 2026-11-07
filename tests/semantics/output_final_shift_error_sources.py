#!/usr/bin/env python3
"""FINAL conversion retains real negative integer shift errors."""
from pathlib import Path
import function_scope as scope

LEFT = b"""<?php
declare(strict_types=0);
echo 'P';
class T {
    function __toString() {
        return 1 << -1;
    }
}
function h($b,$p) { return new T; }
ob_start('h'); echo 'A';
"""
RIGHT = LEFT.replace(b'1 << -1', b'1 >> -1')
CASES = {'native-shift-left-error': LEFT,
         'native-shift-right-error': RIGHT,
         'native-shift-normal': LEFT.replace(b'1 << -1', b'1 << 0')}
CATCH = LEFT.replace(b'        return 1 << -1;',
                     b"        try { return 1 << -1; } catch (ArithmeticError) { return 'H'; }")
OVERRIDE = LEFT.replace(b'        return 1 << -1;',
                        b"        try { return 1 << -1; } finally { return 'H'; }")
CLEANUP = LEFT.replace(b'class T {', b'class D { function __destruct() { echo $missing; } }\nclass T {').replace(
    b'        return 1 << -1;', b'        $d = new D;\n        return 1 << -1;')

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-shift-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
