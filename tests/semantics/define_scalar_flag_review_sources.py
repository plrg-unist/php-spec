#!/usr/bin/env python3
"""Independent raw float flag and abrupt ignored-warning continuation."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'throwing-ignored-warning-keeps-raw-float-flag': br'''<?php
function stopRawScalarFlag31($level, $message) {
    global $name, $value, $flag, $call;
    echo 'H|', $level, '|', $message, '|';
    $name = 'changed';
    $value = 999;
    $flag = '0';
    $call = 'constant';
    throw new Exception('stop');
}
function rawScalarFlagCaller31() {
    global $name, $value, $flag, $call;
    $name = 'RawScalarFlag31';
    $value = 159;
    $flag = 2.5;
    $call = 'define';
    $result = 99;
    set_error_handler('stopRawScalarFlag31');
    try {
        $result = $call(value: $value, case_insensitive: $flag, constant_name: $name);
        echo 'BAD';
    } catch (Exception $e) {
        $trace = $e->getTrace();
        echo $name, '|', $value, '|', $flag === '0' ? 'S' : 'BAD';
        echo '|', $call, '|', $result, '|', $e->getMessage();
        echo '|', $trace[0]['function'], '|', $trace[1]['function'];
        echo '|', $trace[1]['args'][0] === 'RawScalarFlag31' ? 'N' : 'BAD';
        echo '|', $trace[1]['args'][1] === 159 ? 'V' : 'BAD';
        echo '|', $trace[1]['args'][2] === 2.5 ? 'D' : 'BAD';
        echo '|', $trace[2]['function'], '|', defined('RawScalarFlag31') ? 'T' : 'F';
        echo '|', defined('RawScalarFlag31') ? constant('RawScalarFlag31') : 'absent';
        echo '|', defined('changed') ? 'T' : 'F';
    } finally {
        restore_error_handler();
        echo '|Z';
    }
}
echo 'B|';
rawScalarFlagCaller31();
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
