#!/usr/bin/env python3
"""Native-first NULL boolean flags, raw traces and post-deprecation registration."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'literal-null-flag-publication-and-duplicate': br'''<?php
echo 'B|';
echo define('LiteralNullFlag33', 173, null) ? 'T' : 'F';
echo '|', constant('LiteralNullFlag33'), '|';
echo define('LiteralNullFlag33', 174, null) ? 'T' : 'F';
echo '|', constant('LiteralNullFlag33');
''',
    'captured-null-flag-and-callback-created-duplicate': br'''<?php
function nullFlagValue33() {
    global $flag, $call;
    echo 'V|'; $flag = true; $call = 'constant'; return 181;
}
function nullFlagName33() {
    global $flag, $call;
    echo 'N|'; $flag = false; $call = 'defined'; return 'CapturedNullFlag33';
}
function publishThenStopNullFlag33($level, $message) {
    global $name, $value, $flag, $call, $warnings;
    echo 'H|', $level, '|', $message, '|';
    $warnings++;
    if ($warnings === 1) {
        define('CapturedNullFlag33', 281);
        $name = 'changed'; $value = 999; $flag = true; $call = 'constant';
        return true;
    }
    $name = 'again'; $flag = false; $call = 'defined';
    throw new Exception('stop');
}
function nullFlagCaller33() {
    global $name, $value, $flag, $call, $warnings;
    $name = 'CapturedNullFlag33'; $value = 181; $flag = null; $call = 'define'; $warnings = 0;
    $result = 99;
    set_error_handler('publishThenStopNullFlag33');
    try {
        $result = $call(case_insensitive: $flag, value: nullFlagValue33(), constant_name: nullFlagName33());
        echo 'BAD';
    } catch (Exception $e) {
        $trace = $e->getTrace();
        echo $name, '|', $value, '|', $flag === false ? 'F' : 'BAD';
        echo '|', $call, '|', $result, '|', $e->getMessage();
        echo '|', $trace[0]['function'], '|', $trace[1]['function'];
        echo '|', $trace[1]['args'][0] === 'CapturedNullFlag33' ? 'N' : 'BAD';
        echo '|', $trace[1]['args'][1] === 181 ? 'V' : 'BAD';
        echo '|', $trace[1]['args'][2] === null ? 'N' : 'BAD';
        echo '|', $trace[2]['function'], '|', constant('CapturedNullFlag33');
        echo '|', defined('again') ? 'T' : 'F';
    } finally {
        restore_error_handler();
        echo '|Z';
    }
}
echo 'B|';
nullFlagCaller33();
''',
    'strict-null-flag-after-all-argument-effects': br'''<?php
declare(strict_types=1);
function strictNullFlagHandler33($level, $message) { echo 'BAD-H|'; return true; }
function strictNullFlagValue33() { global $flag, $call; echo 'V|'; $flag = true; $call = 'constant'; return 191; }
function strictNullFlagName33() { global $call; echo 'N|'; $call = 'defined'; return 'StrictNullFlag33'; }
$flag = null; $call = 'define'; $result = 99;
set_error_handler('strictNullFlagHandler33');
echo 'B|';
try {
    $result = $call(case_insensitive: $flag, value: strictNullFlagValue33(), constant_name: strictNullFlagName33());
    echo 'BAD';
} catch (TypeError $e) {
    $trace = $e->getTrace();
    echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0] === 'StrictNullFlag33' ? 'N' : 'BAD';
    echo '|', $trace[0]['args'][1] === 191 ? 'V' : 'BAD';
    echo '|', $trace[0]['args'][2] === null ? 'N' : 'BAD';
}
restore_error_handler();
echo '|', $call, '|', $flag === true ? 'T' : 'BAD', '|', $result;
echo '|', defined('StrictNullFlag33') ? 'T' : 'F';
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
