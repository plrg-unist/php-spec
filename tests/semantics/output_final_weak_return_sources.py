#!/usr/bin/env python3
"""Weak FINAL string return rejection and scalar coercion without method CVs."""
from pathlib import Path
import function_scope as scope

WEAK = b"""<?php
declare(strict_types=0);
echo 'P';
class T {
    function __toString() {
        return null;
    }
}
function h($b,$p) { return new T; }
ob_start('h'); echo 'A';
"""

CASES = {
    'weak-null-return-error': WEAK,
    'weak-bool-return-coercion': WEAK.replace(b'return null;', b'return true;'),
}
CATCH = WEAK.replace(b'        return null;',
                     b"        try { return null; } catch (TypeError) { return 'H'; }")
OVERRIDE = WEAK.replace(b'        return null;',
                        b"        try { return null; } finally { return 'H'; }")

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-weak-return', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
