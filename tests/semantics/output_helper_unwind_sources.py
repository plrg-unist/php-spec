#!/usr/bin/env python3
"""Fresh helper throws unwind into the genuine native output consumer."""
from pathlib import Path
import function_scope as scope

CASES = {
    'helper-throw-through-native-cast': b"""<?php
echo 'P';
class D {
    function __destruct() { echo $missing; }
}
class T {
    function __toString() {
        $d = new D;
        return fail();
    }
    function __destruct() { echo 'X'; }
}
function fail() {
    $message = 'E';
    throw new Exception($message);
}
function h($b,$p) { return new T; }
ob_start('h'); echo 'A';
""",
    'helper-throw-through-native-destructor': b"""<?php
echo 'P';
class T {
    function __toString() {
        $local = new T;
        throw new Exception('E');
    }
    function __destruct() { fail(); }
}
function fail() {
    $message = 'F';
    throw new Exception($message);
}
function h($b,$p) { return new T; }
ob_start('h'); echo 'A';
""",
}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-helper-unwind', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
