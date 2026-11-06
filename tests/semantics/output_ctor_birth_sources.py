#!/usr/bin/env python3
"""Completed native-output CTOR_NEW results retain their genuine birth."""
from pathlib import Path
import function_scope as scope

CASES = {
    'string-cv-message': b"""<?php
echo 'P';
class D {
    function __destruct() { echo $missing; }
}
class T {
    function __toString() {
        $message = 'E';
        $d = new D;
        throw new Exception($message);
    }
    function __destruct() { echo 'X'; }
}
function h($b,$p) { return new T; }
ob_start('h'); echo 'A';
""",
    'argument-allocation-before-local-throw': b"""<?php
echo 'P';
class Q {}
class T {
    function __toString() {
        $local = new T;
        throw new Exception('E');
    }
    function __destruct() { throw new Exception(message()); }
}
function message() { $q = new Q; return 'F'; }
function h($b,$p) { return new T; }
ob_start('h'); echo 'A';
""",
}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-ctor-birth', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
