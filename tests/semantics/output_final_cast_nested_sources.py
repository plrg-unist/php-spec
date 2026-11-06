#!/usr/bin/env python3
"""A native FINAL CV destructor fatal aborts before the outer cast returns."""
from pathlib import Path
import function_scope as scope

CASES = {
    'fresh-local-destructor-throw': b"""<?php
echo 'P';
class D {
    function __destruct() { echo 'D'; throw new Exception('F'); }
}
class T {
    function __toString() {
        $d = new D;
        $later = new T;
        throw new Exception('E');
    }
    function __destruct() { echo 'X'; }
}
function h($b,$p) { return new T; }
ob_start('h'); echo 'A';
""",
}
CASES['caught-local-destructor-throw'] = CASES['fresh-local-destructor-throw'].replace(
    b"echo 'D'; throw new Exception('F');",
    b"echo 'D'; try { throw new Exception('F'); } catch (Exception $f) {}")

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-cast-nested', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
