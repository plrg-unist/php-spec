#!/usr/bin/env python3
"""Native-first null-name define reception, publication and warning order."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'literal-null-publication-and-returning-duplicate': br'''<?php
function reportNullDefine30($level, $message) {
    echo 'H|', $level, '|', $message, '|';
    return false;
}
set_error_handler('reportNullDefine30');
echo 'B|';
echo define(null, 130) ? 'T' : 'F';
echo '|', constant('');
echo '|', define(null, 131, false) ? 'T' : 'F';
echo '|', constant('');
restore_error_handler();
''',
    'captured-null-name-and-callback-created-duplicate': br'''<?php
function publishThenStopNullDefine30($level, $message) {
    global $name, $call;
    echo 'H|', $level, '|', $message, '|';
    if ($level === 8192) {
        define('', 230);
        $name = 'changed';
        $call = 'constant';
        return true;
    }
    $name = 'again';
    $call = 'defined';
    throw new Exception('stop');
}
function nullDefineCaller30() {
    global $name, $call;
    $name = null;
    $call = 'define';
    $result = 99;
    set_error_handler('publishThenStopNullDefine30');
    try {
        $result = $call(value: 131, constant_name: $name, case_insensitive: false);
        echo 'BAD';
    } catch (Exception $e) {
        $trace = $e->getTrace();
        echo $name, '|', $call, '|', $result, '|', $e->getMessage();
        echo '|', $trace[0]['function'], '|', $trace[1]['function'];
        echo '|', $trace[1]['args'][0] === '' ? 'S' : 'BAD';
        echo '|', $trace[1]['args'][1] === 131 ? 'V' : 'BAD';
        echo '|', $trace[1]['args'][2] === false ? 'F' : 'BAD';
        echo '|', $trace[2]['function'], '|', constant('');
        echo '|', defined('again') ? 'T' : 'F';
    } finally {
        restore_error_handler();
        echo '|Z';
    }
}
echo 'B|';
nullDefineCaller30();
''',
    'strict-null-define-after-all-argument-effects': br'''<?php
declare(strict_types=1);
function strictNullDefineHandler30($level, $message) { echo 'BAD-H|'; return true; }
function strictNullDefineValue30() { global $call; echo 'V|'; $call = 'constant'; return 137; }
function strictNullDefineName30() { global $call; echo 'N|'; $call = 'defined'; return null; }
$call = 'define';
$result = 99;
set_error_handler('strictNullDefineHandler30');
echo 'B|';
try {
    $result = $call(value: strictNullDefineValue30(), constant_name: strictNullDefineName30(), case_insensitive: false);
    echo 'BAD';
} catch (TypeError $e) {
    $trace = $e->getTrace();
    echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0] === null ? 'N' : 'BAD';
    echo '|', $trace[0]['args'][1] === 137 ? 'V' : 'BAD';
    echo '|', $trace[0]['args'][2] === false ? 'F' : 'BAD';
}
restore_error_handler();
echo '|', $call, '|', $result, '|', defined('') ? 'T' : 'F';
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
