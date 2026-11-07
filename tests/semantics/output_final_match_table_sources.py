#!/usr/bin/env python3
"""FINAL conversion retains a real unmatched integer table dispatch error."""
from pathlib import Path
import function_scope as scope

MISSING = b"""<?php
declare(strict_types=0);
echo 'P';
class T {
    function __toString() {
        return match (3) { 1 => 'H', 2 => 'I' };
    }
}
function h($b,$p) { return new T; }
ob_start('h'); echo 'A';
"""
NORMAL = MISSING.replace(b"match (3)", b"match (1)")
CASES = {'native-match-table-error': MISSING, 'native-match-table-normal': NORMAL}
CATCH = MISSING.replace(b"        return match (3) { 1 => 'H', 2 => 'I' };",
                        b"        try { return match (3) { 1 => 'H', 2 => 'I' }; } catch (UnhandledMatchError) { return 'H'; }")
OVERRIDE = MISSING.replace(b"        return match (3) { 1 => 'H', 2 => 'I' };",
                           b"        try { return match (3) { 1 => 'H', 2 => 'I' }; } finally { return 'H'; }")
CLEANUP = MISSING.replace(b'class T {', b'class D { function __destruct() { echo $missing; } }\nclass T {').replace(
    b"        return match (3) { 1 => 'H', 2 => 'I' };", b"        $d = new D;\n        return match (3) { 1 => 'H', 2 => 'I' };")

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-match-table', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
