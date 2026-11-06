#!/usr/bin/env python3
"""Ordinary native FINAL method CV cleanup precedes default fatal reporting."""
from pathlib import Path
import function_scope as scope

CASES = {
    'fresh-throw-local-warning': b"""<?php
echo 'P';
class D {
    function __destruct() { echo $missing; }
}
class T {
    function __toString() {
        $d = new D;
        throw new Exception('E');
    }
    function __destruct() { echo 'X'; }
}
function h($b,$p) { return new T; }
ob_start('h'); echo 'A';
""",
}
CASES['caught-fresh-normal'] = CASES['fresh-throw-local-warning'].replace(
    b"        throw new Exception('E');",
    b"        try { throw new Exception('E'); } catch (Exception $e) { return 'H'; }")

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-cast-locals', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
