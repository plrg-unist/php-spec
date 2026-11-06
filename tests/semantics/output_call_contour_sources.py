#!/usr/bin/env python3
"""Fresh exceptions traverse the actual finite ordinary helper contour."""
from pathlib import Path
import function_scope as scope

CASES = {
    'multi-level-native-cast': b"""<?php
echo 'P';
class D {
    function __destruct() { echo $missing; }
}
class T {
    function __toString() {
        $d = new D;
        return middle();
    }
    function __destruct() { echo 'X'; }
}
function middle() { $keep = 'M'; return leaf(); }
function leaf() {
    $message = 'E';
    throw new Exception($message);
}
function h($b,$p) { return new T; }
ob_start('h'); echo 'A';
""",
    'recursive-native-destructor': b"""<?php
echo 'P';
$level = 2;
class T {
    function __toString() {
        $local = new T;
        throw new Exception('E');
    }
    function __destruct() { recur(); }
}
function recur() {
    global $level;
    if ($level > 0) { $level = $level - 1; return recur(); }
    $message = 'F';
    throw new Exception($message);
}
function h($b,$p) { return new T; }
ob_start('h'); echo 'A';
""",
}
CASES['intermediate-helper-catch'] = CASES['multi-level-native-cast'].replace(
    b"function middle() { $keep = 'M'; return leaf(); }",
    b"function middle() { $keep = 'M'; try { return leaf(); } catch (Exception $e) { return 'H'; } }")
CASES['intermediate-recursive-normal-override'] = CASES['recursive-native-destructor'].replace(
    b"if ($level > 0) { $level = $level - 1; return recur(); }",
    b"if ($level > 0) { $level = $level - 1; try { return recur(); } finally { return 'H'; } }")

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-call-contour', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
