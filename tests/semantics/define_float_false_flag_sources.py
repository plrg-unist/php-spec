#!/usr/bin/env python3
"""Native-first finite float define names with quiet false scalar flags."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'signed-zero-float-names-false-flags-and-default-duplicate': br'''<?php
echo 'B|';
echo define(-0.0, 701, 0) ? 'T' : 'BAD', '|', constant('-0');
echo '|', define(0.0, 702, '') ? 'T' : 'BAD', '|', constant('0');
echo '|', define(2.5, 703, -0.0) ? 'T' : 'BAD', '|', constant('2.5');
echo '|', define(-0.0, 704, '0') ? 'BAD' : 'F', '|', constant('-0');
echo '|', define(37, 737, 0) ? 'T' : 'BAD', '|', constant('37');
''',
    'captured-request-zero-before-float-name-live-effects': br'''<?php
function floatFalseValue42() {
    global $name, $value, $flag, $call;
    echo 'V|'; $name = 'value-effect'; $value = 997; $flag = 1; $call = 'constant';
    $part = 'captured'; return $part . '-value42';
}
function floatFalseName42() {
    global $name, $flag, $call;
    echo 'N|'; $name = 'name-effect'; $flag = 'false'; $call = 'defined'; return 2.75;
}
function forbiddenFloatFalse42($level, $message) { echo 'BAD-H|'; return true; }
function floatFalseCaller42() {
    global $name, $value, $flag, $call;
    $name = 0; $value = 0; $left = '00'; $mask = '0'; $flag = $left & $mask;
    $call = 'define'; $result = 99;
    set_error_handler('forbiddenFloatFalse42');
    try {
        $result = $call(case_insensitive: $flag, value: floatFalseValue42(), constant_name: floatFalseName42());
        echo $result ? 'T' : 'BAD', '|', constant('2.75');
        echo '|', $name, '|', $value, '|', $flag === 'false' ? 'S' : 'BAD', '|', $call;
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; floatFalseCaller42();
''',
    'strict-float-name-precedes-nonbool-flag-after-effects': br'''<?php
declare(strict_types=1);
function strictFloatFalseValue42() { global $flag, $call; echo 'V|'; $flag = true; $call = 'constant'; return 747; }
function strictFloatFalseName42() { global $call; echo 'N|'; $call = 'defined'; return 2.5; }
function forbiddenStrictFloatFalse42($level, $message) { echo 'BAD-H|'; return true; }
$flag = 0; $call = 'define'; $result = 99;
set_error_handler('forbiddenStrictFloatFalse42');
echo 'B|';
try {
    $result = $call(case_insensitive: $flag, value: strictFloatFalseValue42(), constant_name: strictFloatFalseName42());
    echo 'BAD';
} catch (TypeError $e) {
    $trace = $e->getTrace();
    echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0] === 2.5 ? 'D' : 'BAD', '|', $trace[0]['args'][1];
    echo '|', $trace[0]['args'][2] === 0 ? 'I' : 'BAD';
}
try { $result = define(-0.0, 749, '0'); echo 'BAD'; }
catch (TypeError $e) {
    $trace = $e->getTrace();
    echo '|', $e->getMessage(), '|', $trace[0]['args'][0];
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
