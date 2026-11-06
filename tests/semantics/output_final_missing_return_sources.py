#!/usr/bin/env python3
"""FINAL string conversion verifies a genuine missing native method return."""
from pathlib import Path
import function_scope as scope

MISSING = b"""<?php
declare(strict_types=0);
echo 'P';
class T {
    function __toString() {
    }
}
function h($b,$p) { return new T; }
ob_start('h'); echo 'A';
"""

NORMAL = MISSING.replace(b'    function __toString() {\n',
                         b"    function __toString() {\n        return 'H';\n")
CASES = {'missing-native-return-error': MISSING, 'normal-native-return': NORMAL}
PREVENT = MISSING.replace(b'    function __toString() {\n',
                          b"    function __toString() {\n        try {} finally { return 'H'; }\n")
CLEANUP = MISSING.replace(b'class T {', b'class D { function __destruct() { echo $missing; } }\nclass T {').replace(
    b'    function __toString() {\n', b'    function __toString() {\n        $d = new D;\n')

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-missing-return', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
