#!/usr/bin/env python3
"""FINAL conversion retains quiet integer-operator TypeErrors."""
from pathlib import Path
import function_scope as scope

SHIFT_LEFT = b"""<?php
declare(strict_types=0);
echo 'P';
class T {
    function __toString() {
        return 1 << 'X';
    }
}
function h($b,$p) { return new T; }
ob_start('h'); echo 'A';
"""
SHIFT_RIGHT = SHIFT_LEFT.replace(b"1 << 'X'", b"1 >> 'X'")
BIT_AND = SHIFT_LEFT.replace(b"1 << 'X'", b"1 & 'X'")
BIT_OR = SHIFT_LEFT.replace(b"1 << 'X'", b"1 | 'X'")
BIT_XOR = SHIFT_LEFT.replace(b"1 << 'X'", b"1 ^ 'X'")
NORMAL = SHIFT_LEFT.replace(b"1 << 'X'", b"1 << '2'")
CASES = {'native-left-shift-type-error': SHIFT_LEFT,
         'native-right-shift-type-error': SHIFT_RIGHT,
         'native-bit-and-type-error': BIT_AND,
         'native-bit-or-type-error': BIT_OR,
         'native-bit-xor-type-error': BIT_XOR,
         'native-left-shift-numeric-string': NORMAL}
CATCH = SHIFT_LEFT.replace(b"        return 1 << 'X';",
                           b"        try { return 1 << 'X'; } catch (TypeError) { return 'H'; }")
OVERRIDE = SHIFT_LEFT.replace(b"        return 1 << 'X';",
                              b"        try { return 1 << 'X'; } finally { return 'H'; }")
CLEANUP = SHIFT_LEFT.replace(b'class T {', b'class D { function __destruct() { echo $missing; } }\nclass T {').replace(
    b"        return 1 << 'X';", b"        $d = new D;\n        return 1 << 'X';")

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-integer-type-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
