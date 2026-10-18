#!/usr/bin/env python3
"""Native-first NaN name conversion Warning before protected define duplicate."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'literal-nan-name-conversion-warning-then-startup-duplicate': br'''<?php
echo 'B|';
echo define(NAN, 953) ? 'BAD' : 'F';
echo '|', constant('NAN') !== constant('NAN') ? 'N' : 'BAD';
''',
    'captured-nan-name-precision-change-before-second-warning-throw': br'''<?php
function nanNameValue46() {
    global $name, $candidate, $flag, $call;
    echo 'V|'; $name = INF; $candidate = 997; $flag = true; $call = 'constant';
    $part = 'outer'; return $part . '-value46';
}
function nanNameArgument46() {
    global $name, $call;
    echo 'N|'; $name = 2.5; $call = 'defined'; return NAN;
}
function throwSecondNanName46($level, $message) {
    global $name, $candidate, $flag, $call, $count, $pending;
    echo 'H|', $level, '|', $message, '|'; $count++;
    if ($count === 1) {
        ini_set('precision', '1'); define('NanNameSibling46', 971);
        $name = 9.5; $candidate = 991; $flag = true; $call = 'constant'; return true;
    }
    $pending = new Exception('nan-name-second'); throw $pending;
}
function nanNameCaller46() {
    global $name, $candidate, $flag, $call, $count, $pending;
    $name = 0; $candidate = 0; $flag = false; $call = 'define'; $count = 0; $pending = null; $result = 99;
    set_error_handler('throwSecondNanName46');
    try {
        $result = $call(case_insensitive: $flag, value: nanNameValue46(), constant_name: nanNameArgument46());
        echo 'BAD';
    } catch (Exception $e) {
        $trace = $e->getTrace();
        echo $count, '|', $result, '|', $e === $pending ? 'I' : 'BAD';
        echo '|', $e->getPrevious() === null ? 'P' : 'BAD';
        echo '|', $trace[1]['args'][0] === 'NAN' ? 'S' : 'BAD';
        echo '|', $trace[1]['args'][1] === 'outer-value46' ? 'V' : 'BAD';
        echo '|', $trace[1]['args'][2] === false ? 'F' : 'BAD';
        echo '|', constant('NAN') !== constant('NAN') ? 'N' : 'BAD';
        echo '|', constant('NanNameSibling46'), '|', $candidate, '|', $flag === true ? 'T' : 'BAD';
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; nanNameCaller46();
''',
    'strict-nan-name-error-before-conversion-warning': br'''<?php
declare(strict_types=1);
function strictNanNameValue46() { global $flag, $call; echo 'V|'; $flag = true; $call = 'constant'; return 977; }
function strictNanNameArgument46() { global $call; echo 'N|'; $call = 'defined'; return NAN; }
function forbiddenNanName46($level, $message) { echo 'BAD-H|'; return true; }
$flag = false; $call = 'define'; $result = 99;
set_error_handler('forbiddenNanName46');
echo 'B|';
try {
    $result = $call(case_insensitive: $flag, value: strictNanNameValue46(), constant_name: strictNanNameArgument46());
    echo 'BAD';
} catch (TypeError $e) {
    $trace = $e->getTrace();
    echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0] !== $trace[0]['args'][0] ? 'N' : 'BAD';
    echo '|', $trace[0]['args'][1], '|', $trace[0]['args'][2] === false ? 'F' : 'BAD';
}
restore_error_handler();
echo '|', $flag === true ? 'T' : 'BAD', '|', $call, '|', $result;
''',
}
family.BASELINE = ('scalar define publication', b'B|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
