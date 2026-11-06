#!/usr/bin/env python3
"""Generated FINAL string return errors without compiled method CVs."""
from pathlib import Path
import function_scope as scope

STRICT = b"""<?php
declare(strict_types=1);
echo 'P';
class T {
    function __toString() {
        return 42;
    }
}
function h($b,$p) { return new T; }
ob_start('h'); echo 'A';
"""

CASES = {
    'empty-strict-return-error': STRICT,
    'empty-weak-return-coercion': STRICT.replace(b'strict_types=1', b'strict_types=0'),
}
CATCH = STRICT.replace(b'        return 42;',
                       b"        try { return 42; } catch (TypeError) { return 'H'; }")
OVERRIDE = STRICT.replace(b'        return 42;',
                          b"        try { return 42; } finally { return 'H'; }")

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-empty-return', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
