#!/usr/bin/env python3
"""Native-first NULL define names with quiet false scalar third flags."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'literal-null-names-false-flags-and-default-duplicates': br'''<?php
echo 'B|';
echo define(null, 601, 0) ? 'T' : 'BAD', '|', constant('');
echo '|', define(null, 602, '') ? 'BAD' : 'F', '|', constant('');
echo '|', define(null, 603, -0.0) ? 'BAD' : 'F', '|', constant('');
echo '|', define(null, 604, '0') ? 'BAD' : 'F', '|', constant('');
''',
    'captured-null-and-request-zero-through-returning-handlers': br'''<?php
function nullFalseValue41() {
    global $flag, $call;
    echo 'V|'; $flag = 1; $call = 'constant';
    $part = 'captured'; return $part . '-value41';
}
function nullFalseName41() {
    global $flag, $call;
    echo 'N|'; $flag = 'false'; $call = 'defined'; return null;
}
function reportNullFalse41($level, $message) {
    global $name, $value, $flag, $call, $count;
    $count = $count + 1;
    echo 'H|', $level, '|', $message, '|';
    if ($level === 8192) {
        define('', 613);
        $name = 'handler-name'; $value = 'handler-value'; $flag = true; $call = 'constant';
    }
    return true;
}
function nullFalseCaller41() {
    global $name, $value, $flag, $call, $count;
    $name = 0; $value = 0; $left = '00'; $mask = '0'; $flag = $left & $mask;
    $call = 'define'; $result = 99; $count = 0;
    set_error_handler('reportNullFalse41');
    try {
        $result = $call(case_insensitive: $flag, value: nullFalseValue41(), constant_name: nullFalseName41());
        echo $result === false ? 'F' : 'BAD', '|', constant('');
        echo '|', $name, '|', $value, '|', $flag === true ? 'T' : 'BAD';
        echo '|', $call, '|', $count;
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; nullFalseCaller41();
''',
    'strict-null-name-precedes-nonbool-flag-after-effects': br'''<?php
declare(strict_types=1);
function strictNullFalseValue41() { global $flag, $call; echo 'V|'; $flag = true; $call = 'constant'; return 647; }
function strictNullFalseName41() { global $call; echo 'N|'; $call = 'defined'; return null; }
function forbiddenStrictNullFalse41($level, $message) { echo 'BAD-H|'; return true; }
$flag = 0; $call = 'define'; $result = 99;
set_error_handler('forbiddenStrictNullFalse41');
echo 'B|';
try {
    $result = $call(case_insensitive: $flag, value: strictNullFalseValue41(), constant_name: strictNullFalseName41());
    echo 'BAD';
} catch (TypeError $e) {
    $trace = $e->getTrace();
    echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0] === null ? 'N' : 'BAD', '|', $trace[0]['args'][1];
    echo '|', $trace[0]['args'][2] === 0 ? 'I' : 'BAD';
}
try { $result = define(null, 649, -0.0); echo 'BAD'; }
catch (TypeError $e) {
    $trace = $e->getTrace();
    echo '|', $e->getMessage(), '|', $trace[0]['args'][0] === null ? 'N' : 'BAD';
    echo '|', $trace[0]['args'][2] === -0.0 ? 'Z' : 'BAD';
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
