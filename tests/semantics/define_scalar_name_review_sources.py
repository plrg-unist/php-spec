#!/usr/bin/env python3
"""Independent converted define name retained across a throwing warning handler."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'float-duplicate-throw-after-precision-change': br'''<?php
function rejectFloatDuplicate28($level, $message) {
    echo 'H|', $level, '|', $message, '|';
    ini_set('precision', '1');
    throw new Exception('stop');
}
function duplicateFloatCaller28() {
    define('2.5', 125);
    $name = 2.5;
    $result = 99;
    $call = 'define';
    set_error_handler('rejectFloatDuplicate28');
    try {
        $result = $call(value: 29, constant_name: $name, case_insensitive: false);
        echo 'BAD';
    } catch (Exception $e) {
        $trace = $e->getTrace();
        echo $name === 2.5 ? 'D' : 'BAD';
        echo '|', $result, '|', $e->getMessage();
        echo '|', $trace[0]['function'], '|', $trace[1]['function'];
        echo '|', $trace[1]['args'][0] === '2.5' ? 'S' : 'BAD';
        echo '|', $trace[1]['args'][1] === 29 ? 'V' : 'BAD';
        echo '|', $trace[2]['function'];
        echo '|', constant('2.5'), '|', defined('2') ? 'T' : 'F';
    } finally {
        restore_error_handler();
        echo '|Z';
    }
}
echo 'B|';
duplicateFloatCaller28();
''',
}
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
