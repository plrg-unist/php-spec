#!/usr/bin/env python3
"""FINAL conversion retains a real unmatched scalar match error."""
from pathlib import Path
import function_scope as scope

MISSING = b"""<?php
declare(strict_types=0);
echo 'P';
class T {
    function __toString() {
        return match (1) { 2 => 'H' };
    }
}
function h($b,$p) { return new T; }
ob_start('h'); echo 'A';
"""
NORMAL = MISSING.replace(b"2 => 'H'", b"1 => 'H'")
CASES = {'native-match-error': MISSING, 'native-match-normal': NORMAL}
CATCH = MISSING.replace(b"        return match (1) { 2 => 'H' };",
                        b"        try { return match (1) { 2 => 'H' }; } catch (UnhandledMatchError) { return 'H'; }")
OVERRIDE = MISSING.replace(b"        return match (1) { 2 => 'H' };",
                           b"        try { return match (1) { 2 => 'H' }; } finally { return 'H'; }")
CLEANUP = MISSING.replace(b'class T {', b'class D { function __destruct() { echo $missing; } }\nclass T {').replace(
    b"        return match (1) { 2 => 'H' };", b"        $d = new D;\n        return match (1) { 2 => 'H' };")

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-match-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
