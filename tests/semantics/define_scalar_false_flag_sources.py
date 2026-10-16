#!/usr/bin/env python3
"""Native-first int/bool define names with quiet false scalar flags."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'fresh-scalar-names-false-flags-and-default-duplicate': br'''<?php
echo 'B|';
echo define(37, 401, 0) ? 'T' : 'BAD';
echo '|', constant('37');
echo '|', define(false, 402, '0') ? 'T' : 'BAD', '|', constant('');
echo '|', define(true, 403, -0.0) ? 'T' : 'BAD', '|', constant('1');
echo '|', define(2, 404, '') ? 'T' : 'BAD', '|', constant('2');
echo '|', define(37, 405, 0) ? 'BAD' : 'F', '|', constant('37');
''',
    'captured-request-zero-before-live-truthy-flag-effects': br'''<?php
function scalarFalseValue40() {
    global $name, $value, $flag, $call;
    echo 'V|'; $name = 'value-effect'; $value = 997; $flag = 1; $call = 'constant';
    $part = 'captured'; return $part . '-value40';
}
function scalarFalseName40() {
    global $name, $flag, $call;
    echo 'N|'; $name = 'name-effect'; $flag = 'false'; $call = 'defined'; return 42;
}
function forbiddenScalarFalseWarning40($level, $message) { echo 'BAD-H|'; return true; }
function scalarFalseCaller40() {
    global $name, $value, $flag, $call;
    $name = 0; $value = 0; $left = '00'; $mask = '0'; $flag = $left & $mask;
    $call = 'define'; $result = 99;
    set_error_handler('forbiddenScalarFalseWarning40');
    try {
        $result = $call(case_insensitive: $flag, value: scalarFalseValue40(), constant_name: scalarFalseName40());
        echo $result ? 'T' : 'BAD', '|', constant('42');
        echo '|', $name, '|', $value, '|', $flag === 'false' ? 'S' : 'BAD', '|', $call;
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; scalarFalseCaller40();
''',
    'strict-name-error-precedes-nonbool-flag-after-effects': br'''<?php
declare(strict_types=1);
function strictScalarFalseValue40() { global $flag, $call; echo 'V|'; $flag = true; $call = 'constant'; return 447; }
function strictScalarFalseName40() { global $call; echo 'N|'; $call = 'defined'; return 47; }
function forbiddenStrictFalseWarning40($level, $message) { echo 'BAD-H|'; return true; }
$flag = 0; $call = 'define'; $result = 99;
set_error_handler('forbiddenStrictFalseWarning40');
echo 'B|';
try {
    $result = $call(case_insensitive: $flag, value: strictScalarFalseValue40(), constant_name: strictScalarFalseName40());
    echo 'BAD';
} catch (TypeError $e) {
    $trace = $e->getTrace();
    echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0] === 47 ? 'I' : 'BAD', '|', $trace[0]['args'][1];
    echo '|', $trace[0]['args'][2] === 0 ? 'I' : 'BAD';
}
try { $result = define(false, 449, '0'); echo 'BAD'; }
catch (TypeError $e) {
    $trace = $e->getTrace();
    echo '|', $e->getMessage(), '|', $trace[0]['args'][0] === false ? 'F' : 'BAD';
    echo '|', $trace[0]['args'][2] === '0' ? 'S' : 'BAD';
}
restore_error_handler();
echo '|', $flag === true ? 'T' : 'BAD', '|', $call, '|', $result;
''',
}
family.BASELINE = ('dynamic constant call domain', b'B|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
