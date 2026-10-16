#!/usr/bin/env python3
"""Native-first NaN bool warning precedes the class-name define error."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'literal-nan-flag-conversion-warning-before-class-name-error': br'''<?php
$result = 99;
echo 'B|';
try { $result = define('Literal::Nan39', 433, NAN); echo 'BAD'; }
catch (ValueError $e) {
    $trace = $e->getTrace();
    echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0], '|', $trace[0]['args'][1];
    echo '|', $trace[0]['args'][2] !== $trace[0]['args'][2] ? 'N' : 'BAD', '|', $result;
}
''',
    'captured-nan-flag-handler-return-then-class-name-error': br'''<?php
function classNanValue39() {
    global $value, $flag, $call;
    echo 'V|'; $value = 937; $flag = true; $call = 'constant';
    $part = 'captured'; return $part . '-value39';
}
function classNanName39() {
    global $name, $flag, $call;
    echo 'N|'; $name = 'name-effect'; $flag = false; $call = 'defined';
    $part = 'Captured'; return $part . '::Nan39';
}
function returnClassNanWarning39($level, $message) {
    global $name, $value, $flag, $call, $warnings;
    echo 'H|', $level, '|', $message, '|';
    $warnings++;
    define('ClassNanInner39', 458);
    $name = 'LivePlain39'; $value = 938; $flag = true; $call = 'constant';
    return false;
}
function classNanCaller39() {
    global $name, $value, $flag, $call, $warnings;
    $name = 'before'; $value = 0; $flag = NAN; $call = 'define'; $warnings = 0; $result = 99;
    set_error_handler('returnClassNanWarning39');
    try {
        $result = $call(case_insensitive: $flag, value: classNanValue39(), constant_name: classNanName39());
        echo 'BAD';
    } catch (ValueError $e) {
        $trace = $e->getTrace();
        echo $e->getMessage(), '|', $e->getLine(), '|', $e->getPrevious() === null ? 'P' : 'BAD';
        echo '|', $trace[0]['function'], '|', $trace[0]['args'][0], '|', $trace[0]['args'][1];
        echo '|', $trace[0]['args'][2] !== $trace[0]['args'][2] ? 'N' : 'BAD', '|', $trace[1]['function'];
        echo '|', $name, '|', $value, '|', $flag === true ? 'T' : 'BAD', '|', $call;
        echo '|', $result, '|', $warnings, '|', constant('ClassNanInner39');
        echo '|', defined('LivePlain39') ? 'BAD' : 'F';
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; classNanCaller39();
''',
    'strict-nan-flag-before-conversion-warning-and-class-name-error': br'''<?php
declare(strict_types=1);
function strictClassNanValue39() { global $flag, $call; echo 'V|'; $flag = true; $call = 'constant'; return 447; }
function strictClassNanName39() { global $call; echo 'N|'; $call = 'defined'; return 'Strict::Nan39'; }
function forbiddenStrictClassNan39($level, $message) { echo 'BAD-H|'; return true; }
$flag = NAN; $call = 'define'; $result = 99;
set_error_handler('forbiddenStrictClassNan39');
echo 'B|';
try {
    $result = $call(case_insensitive: $flag, value: strictClassNanValue39(), constant_name: strictClassNanName39());
    echo 'BAD';
} catch (TypeError $e) {
    $trace = $e->getTrace();
    echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0], '|', $trace[0]['args'][1];
    echo '|', $trace[0]['args'][2] !== $trace[0]['args'][2] ? 'N' : 'BAD';
}
restore_error_handler();
echo '|', $flag === true ? 'T' : 'BAD', '|', $call, '|', $result;
''',
}
family.BASELINE = ('NaN define flag reception', b'B|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
