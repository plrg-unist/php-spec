#!/usr/bin/env python3
"""Independent abrupt null-name define reception before publication."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'throwing-deprecation-keeps-raw-null-definition': br'''<?php
function stopRawNullDefine30($level, $message) {
    global $name, $value, $call;
    echo 'H|', $level, '|', $message, '|';
    $name = 'changed';
    $value = 999;
    $call = 'constant';
    throw new Exception('stop');
}
function rawNullDefineCaller30() {
    global $name, $value, $call;
    $name = null;
    $value = 139;
    $call = 'define';
    $result = 99;
    set_error_handler('stopRawNullDefine30');
    try {
        $result = $call(value: $value, case_insensitive: false, constant_name: $name);
        echo 'BAD';
    } catch (Exception $e) {
        $trace = $e->getTrace();
        echo $name, '|', $value, '|', $call, '|', $result, '|', $e->getMessage();
        echo '|', $trace[0]['function'], '|', $trace[1]['function'];
        echo '|', $trace[1]['args'][0] === null ? 'N' : 'BAD';
        echo '|', $trace[1]['args'][1] === 139 ? 'V' : 'BAD';
        echo '|', $trace[1]['args'][2] === false ? 'F' : 'BAD';
        echo '|', $trace[2]['function'], '|', defined('') ? 'T' : 'F';
        echo '|', defined('changed') ? 'T' : 'F';
    } finally {
        restore_error_handler();
        echo '|Z';
    }
}
echo 'B|';
rawNullDefineCaller30();
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
