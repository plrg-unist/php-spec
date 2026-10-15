#!/usr/bin/env python3
"""Native-first scalar define flags, captured raw arguments and strict errors."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'weak-scalar-flags-and-historical-rows': br'''<?php
function reportScalarFlag31($level, $message) {
    echo 'H|', $level, '|', $message, '|';
    return true;
}
set_error_handler('reportScalarFlag31');
$flag = '0';
echo 'B|';
echo define('FlagStringZero31', 131, $flag) ? 'T' : 'F';
echo '|', $flag === '0' ? 'S' : 'BAD', '|', constant('FlagStringZero31'), '|';
echo define('FlagStringFalse31', 132, 'false') ? 'T' : 'F';
echo '|', constant('FlagStringFalse31'), '|';
echo define('FlagIntZero31', 133, 0) ? 'T' : 'F';
echo '|', constant('FlagIntZero31'), '|';
echo define('FlagIntNonzero31', 134, -2) ? 'T' : 'F';
echo '|', constant('FlagIntNonzero31'), '|';
echo define('FlagFloatZero31', 135, 0.0) ? 'T' : 'F';
echo '|', constant('FlagFloatZero31'), '|';
echo define('FlagFloatNonzero31', 136, 2.5) ? 'T' : 'F';
echo '|', constant('FlagFloatNonzero31'), '|';
$part = 'fal';
$request = $part . 'se';
echo define('FlagRequest31', 137, $request) ? 'T' : 'F';
echo '|', $request === 'false' ? 'S' : 'BAD', '|', constant('FlagRequest31');
echo '|', defined('flagStringFalse31') ? 'BAD' : 'C';
restore_error_handler();
''',
    'captured-flag-and-callback-created-duplicate': br'''<?php
function scalarFlagValue31() {
    global $flag, $call;
    echo 'V|'; $flag = '0'; $call = 'defined'; return 147;
}
function scalarFlagName31() {
    global $flag, $call;
    echo 'N|'; $flag = 0; $call = 'constant'; return 'CapturedFlag31';
}
function publishThenStopFlag31($level, $message) {
    global $name, $value, $flag, $call, $warnings;
    echo 'H|', $level, '|', $message, '|';
    $warnings++;
    if ($warnings === 1) {
        define('CapturedFlag31', 247);
        $name = 'changed'; $value = 999; $flag = '0'; $call = 'constant';
        return false;
    }
    $name = 'again'; $flag = 0; $call = 'defined';
    throw new Exception('stop');
}
function scalarFlagCaller31() {
    global $name, $value, $flag, $call, $warnings;
    $name = 'CapturedFlag31'; $value = 147; $flag = 'false'; $call = 'define'; $warnings = 0;
    $result = 99;
    set_error_handler('publishThenStopFlag31');
    try {
        $result = $call(case_insensitive: $flag, value: scalarFlagValue31(), constant_name: scalarFlagName31());
        echo 'BAD';
    } catch (Exception $e) {
        $trace = $e->getTrace();
        echo $name, '|', $value, '|', $flag === 0 ? 'I' : 'BAD', '|', $call, '|', $result, '|', $e->getMessage();
        echo '|', $trace[0]['function'], '|', $trace[1]['function'];
        echo '|', $trace[1]['args'][0] === 'CapturedFlag31' ? 'N' : 'BAD';
        echo '|', $trace[1]['args'][1] === 147 ? 'V' : 'BAD';
        echo '|', $trace[1]['args'][2] === 'false' ? 'S' : 'BAD';
        echo '|', $trace[2]['function'], '|', constant('CapturedFlag31');
        echo '|', defined('again') ? 'T' : 'F';
    } finally {
        restore_error_handler(); echo '|Z';
    }
}
echo 'B|';
scalarFlagCaller31();
''',
    'strict-flag-errors-after-all-argument-effects': br'''<?php
declare(strict_types=1);
function strictScalarFlagHandler31($level, $message) { echo 'BAD-H|'; return true; }
function strictScalarFlagValue31() { global $flag, $call; echo 'V|'; $flag = 'false'; $call = 'constant'; return 151; }
function strictScalarFlagName31() { global $call; echo 'N|'; $call = 'defined'; return 'StrictIntFlag31'; }
$flag = 0; $call = 'define'; $result = 99;
set_error_handler('strictScalarFlagHandler31');
echo 'B|';
try {
    $result = $call(case_insensitive: $flag, value: strictScalarFlagValue31(), constant_name: strictScalarFlagName31());
    echo 'BAD';
} catch (TypeError $e) {
    $trace = $e->getTrace();
    echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][2] === 0 ? 'I' : 'BAD';
}
try { $result = define('StrictStringFlag31', 152, 'false'); echo 'BAD'; }
catch (TypeError $e) {
    $trace = $e->getTrace();
    echo '|', $e->getMessage(), '|', $trace[0]['args'][2] === 'false' ? 'S' : 'BAD';
}
try { $result = define('StrictFloatFlag31', 153, 2.5); echo 'BAD'; }
catch (TypeError $e) {
    $trace = $e->getTrace();
    echo '|', $e->getMessage(), '|', $trace[0]['args'][2] === 2.5 ? 'D' : 'BAD';
}
restore_error_handler();
echo '|', $call, '|', $flag === 'false' ? 'S' : 'BAD', '|', $result;
echo '|', defined('StrictIntFlag31') ? 'T' : 'F';
echo defined('StrictStringFlag31') ? 'T' : 'F';
echo defined('StrictFloatFlag31') ? 'T' : 'F';
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
