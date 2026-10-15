#!/usr/bin/env python3
"""Native-first class-name errors follow quiet scalar flag reception."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'literal-class-names-with-quiet-scalar-flags': br'''<?php
function forbiddenClassScalarWarning37($level, $message) { echo 'BAD-H|'; return true; }
set_error_handler('forbiddenClassScalarWarning37');
$result = 99;
echo 'B|';
try { $result = define('Int::Bad37', 317, 2); echo 'BAD'; }
catch (ValueError $e) {
    $trace = $e->getTrace();
    echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0], '|', $trace[0]['args'][1];
    echo '|', $trace[0]['args'][2] === 2 ? 'I' : 'BAD';
}
try { $result = define('String::Bad37', 318, 'false'); echo 'BAD'; }
catch (ValueError $e) {
    $trace = $e->getTrace();
    echo '|', $e->getMessage(), '|', $trace[0]['args'][0], '|', $trace[0]['args'][1];
    echo '|', $trace[0]['args'][2] === 'false' ? 'S' : 'BAD';
}
try { $result = define('Float::Bad37', 319, 2.5); echo 'BAD'; }
catch (ValueError $e) {
    $trace = $e->getTrace();
    echo '|', $e->getMessage(), '|', $trace[0]['args'][0], '|', $trace[0]['args'][1];
    echo '|', $trace[0]['args'][2] === 2.5 ? 'D' : 'BAD';
}
restore_error_handler();
echo '|', $result;
''',
    'captured-scalar-flag-before-class-name-error': br'''<?php
function classScalarValue37() {
    global $name, $flag, $call;
    echo 'V|'; $name = 'value-effect'; $flag = false; $call = 'constant'; return 323;
}
function classScalarName37() {
    global $name, $flag, $call;
    echo 'N|'; $name = 'name-effect'; $flag = 0; $call = 'defined';
    $part = 'Captured'; return $part . '::Scalar37';
}
function forbiddenCapturedScalarWarning37($level, $message) { echo 'BAD-H|'; return true; }
function classScalarCaller37() {
    global $name, $flag, $call;
    $name = 'before'; $part = 'fal'; $flag = $part . 'se'; $call = 'define'; $result = 99;
    set_error_handler('forbiddenCapturedScalarWarning37');
    try {
        $result = $call(case_insensitive: $flag, value: classScalarValue37(), constant_name: classScalarName37());
        echo 'BAD';
    } catch (ValueError $e) {
        $trace = $e->getTrace();
        echo $e->getMessage(), '|', $e->getLine(), '|', $e->getPrevious() === null ? 'P' : 'BAD';
        echo '|', $trace[0]['function'], '|', $trace[0]['args'][0], '|', $trace[0]['args'][1];
        echo '|', $trace[0]['args'][2] === 'false' ? 'S' : 'BAD', '|', $trace[1]['function'];
        echo '|', $name, '|', $flag === 0 ? 'I' : 'BAD', '|', $call, '|', $result;
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; classScalarCaller37();
''',
    'strict-scalar-flag-precedes-class-name-error': br'''<?php
declare(strict_types=1);
function strictClassScalarValue37() { global $flag, $call; echo 'V|'; $flag = true; $call = 'constant'; return 329; }
function strictClassScalarName37() { global $call; echo 'N|'; $call = 'defined'; return 'Strict::Bad37'; }
function forbiddenStrictScalarWarning37($level, $message) { echo 'BAD-H|'; return true; }
$flag = 2; $call = 'define'; $result = 99;
set_error_handler('forbiddenStrictScalarWarning37');
echo 'B|';
try {
    $result = $call(case_insensitive: $flag, value: strictClassScalarValue37(), constant_name: strictClassScalarName37());
    echo 'BAD';
} catch (TypeError $e) {
    $trace = $e->getTrace();
    echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0], '|', $trace[0]['args'][1];
    echo '|', $trace[0]['args'][2] === 2 ? 'I' : 'BAD';
}
try { $result = define('Strict::String37', 330, 'false'); echo 'BAD'; }
catch (TypeError $e) {
    $trace = $e->getTrace();
    echo '|', $e->getMessage(), '|', $trace[0]['args'][2] === 'false' ? 'S' : 'BAD';
}
try { $result = define('Strict::Float37', 331, 2.5); echo 'BAD'; }
catch (TypeError $e) {
    $trace = $e->getTrace();
    echo '|', $e->getMessage(), '|', $trace[0]['args'][2] === 2.5 ? 'D' : 'BAD';
}
restore_error_handler();
echo '|', $flag === true ? 'T' : 'BAD', '|', $call, '|', $result;
''',
}
family.BASELINE = ('scalar define flag reception', b'B|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
