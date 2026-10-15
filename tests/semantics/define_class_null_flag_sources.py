#!/usr/bin/env python3
"""Native-first NULL flag deprecation precedes the class-name define error."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'literal-null-flag-deprecation-before-class-name-error': br'''<?php
$result = 99;
echo 'B|';
try { $result = define('Literal::Null38', 383, null); echo 'BAD'; }
catch (ValueError $e) {
    $trace = $e->getTrace();
    echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0], '|', $trace[0]['args'][1];
    echo '|', $trace[0]['args'][2] === null ? 'N' : 'BAD', '|', $result;
}
''',
    'captured-null-flag-handler-return-then-class-name-error': br'''<?php
function classNullValue38() {
    global $value, $flag, $call;
    echo 'V|'; $value = 887; $flag = true; $call = 'constant';
    $part = 'captured'; return $part . '-value38';
}
function classNullName38() {
    global $name, $flag, $call;
    echo 'N|'; $name = 'name-effect'; $flag = false; $call = 'defined';
    $part = 'Captured'; return $part . '::Null38';
}
function returnClassNullWarning38($level, $message) {
    global $name, $value, $flag, $call, $warnings;
    echo 'H|', $level, '|', $message, '|';
    $warnings++;
    define('ClassNullInner38', 408);
    $name = 'LivePlain38'; $value = 888; $flag = true; $call = 'constant';
    return true;
}
function classNullCaller38() {
    global $name, $value, $flag, $call, $warnings;
    $name = 'before'; $value = 0; $flag = null; $call = 'define'; $warnings = 0; $result = 99;
    set_error_handler('returnClassNullWarning38');
    try {
        $result = $call(case_insensitive: $flag, value: classNullValue38(), constant_name: classNullName38());
        echo 'BAD';
    } catch (ValueError $e) {
        $trace = $e->getTrace();
        echo $e->getMessage(), '|', $e->getLine(), '|', $e->getPrevious() === null ? 'P' : 'BAD';
        echo '|', $trace[0]['function'], '|', $trace[0]['args'][0], '|', $trace[0]['args'][1];
        echo '|', $trace[0]['args'][2] === null ? 'N' : 'BAD', '|', $trace[1]['function'];
        echo '|', $name, '|', $value, '|', $flag === true ? 'T' : 'BAD', '|', $call;
        echo '|', $result, '|', $warnings, '|', constant('ClassNullInner38');
        echo '|', defined('LivePlain38') ? 'BAD' : 'F';
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; classNullCaller38();
''',
    'strict-null-flag-before-deprecation-and-class-name-error': br'''<?php
declare(strict_types=1);
function strictClassNullValue38() { global $flag, $call; echo 'V|'; $flag = true; $call = 'constant'; return 397; }
function strictClassNullName38() { global $call; echo 'N|'; $call = 'defined'; return 'Strict::Null38'; }
function forbiddenStrictClassNull38($level, $message) { echo 'BAD-H|'; return true; }
$flag = null; $call = 'define'; $result = 99;
set_error_handler('forbiddenStrictClassNull38');
echo 'B|';
try {
    $result = $call(case_insensitive: $flag, value: strictClassNullValue38(), constant_name: strictClassNullName38());
    echo 'BAD';
} catch (TypeError $e) {
    $trace = $e->getTrace();
    echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0], '|', $trace[0]['args'][1];
    echo '|', $trace[0]['args'][2] === null ? 'N' : 'BAD';
}
restore_error_handler();
echo '|', $flag === true ? 'T' : 'BAD', '|', $call, '|', $result;
''',
}
family.BASELINE = ('null define flag reception', b'B|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
