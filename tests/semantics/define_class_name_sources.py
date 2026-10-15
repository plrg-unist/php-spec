#!/usr/bin/env python3
"""Native-first class-qualified define names fail before ignored-flag warnings."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'literal-class-names-omitted-and-bool-flags': br'''<?php
function forbiddenClassNameWarning36($level, $message) { echo 'BAD-H|'; return true; }
set_error_handler('forbiddenClassNameWarning36');
$result = 99;
echo 'B|';
try { $result = define('A::B36', 211); echo 'BAD'; }
catch (ValueError $e) {
    $trace = $e->getTrace();
    echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0], '|', $trace[0]['args'][1];
    echo '|', isset($trace[0]['args'][2]) ? 'BAD' : 'O';
}
try { $result = define('C::D36', 212, false); echo 'BAD'; }
catch (ValueError $e) {
    $trace = $e->getTrace();
    echo '|', $trace[0]['args'][0], '|', $trace[0]['args'][1];
    echo '|', $trace[0]['args'][2] === false ? 'F' : 'BAD';
}
try { $result = define('E::F36', 213, true); echo 'BAD'; }
catch (ValueError $e) {
    $trace = $e->getTrace();
    echo '|', $e->getMessage(), '|', $trace[0]['args'][0], '|', $trace[0]['args'][1];
    echo '|', $trace[0]['args'][2] === true ? 'T' : 'BAD';
}
restore_error_handler();
echo '|', $result;
''',
    'captured-class-name-before-ignored-true-warning': br'''<?php
function classNameValue36() {
    global $name, $flag, $call;
    echo 'V|'; $name = 'value-effect'; $flag = false; $call = 'constant'; return 223;
}
function classNameName36() {
    global $name, $call;
    echo 'N|'; $name = 'name-effect'; $call = 'defined';
    $part = 'Captured'; return $part . '::Flag36';
}
function forbiddenCapturedClassWarning36($level, $message) { echo 'BAD-H|'; return true; }
function classNameCaller36() {
    global $name, $flag, $call;
    $name = 'before'; $flag = true; $call = 'define'; $result = 99;
    set_error_handler('forbiddenCapturedClassWarning36');
    try {
        $result = $call(case_insensitive: $flag, value: classNameValue36(), constant_name: classNameName36());
        echo 'BAD';
    } catch (ValueError $e) {
        $trace = $e->getTrace();
        echo $e->getMessage(), '|', $e->getLine(), '|', $e->getPrevious() === null ? 'P' : 'BAD';
        echo '|', $trace[0]['function'], '|', $trace[0]['args'][0], '|', $trace[0]['args'][1];
        echo '|', $trace[0]['args'][2] === true ? 'T' : 'BAD', '|', $trace[1]['function'];
        echo '|', $name, '|', $flag === false ? 'F' : 'BAD', '|', $call, '|', $result;
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; classNameCaller36();
''',
    'strict-class-name-after-all-argument-effects': br'''<?php
declare(strict_types=1);
function strictClassNameValue36() { global $flag, $call; echo 'V|'; $flag = true; $call = 'constant'; return 229; }
function strictClassNameName36() { global $call; echo 'N|'; $call = 'defined'; return 'Strict::Bad36'; }
function forbiddenStrictClassWarning36($level, $message) { echo 'BAD-H|'; return true; }
$flag = false; $call = 'define'; $result = 99;
set_error_handler('forbiddenStrictClassWarning36');
echo 'B|';
try {
    $result = $call(case_insensitive: $flag, value: strictClassNameValue36(), constant_name: strictClassNameName36());
    echo 'BAD';
} catch (ValueError $e) {
    $trace = $e->getTrace();
    echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0], '|', $trace[0]['args'][1];
    echo '|', $trace[0]['args'][2] === false ? 'F' : 'BAD';
}
try { $result = define('Strict::True36', 230, true); echo 'BAD'; }
catch (ValueError $e) { echo '|', $e->getMessage(); }
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
