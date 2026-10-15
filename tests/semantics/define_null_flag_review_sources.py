#!/usr/bin/env python3
"""Observe cancellation at the first NULL-flag deprecation after callback writes."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'throwing-null-flag-deprecation-keeps-raw-call': br'''<?php
function stopNullFlag33($level, $message) {
    global $name, $value, $flag, $call;
    echo 'H|', $level, '|', $message, '|';
    define('NullFlagSibling33', 293);
    $name = 'changed'; $value = 999; $flag = true; $call = 'constant';
    throw new Exception('first-stop');
}
function rawNullFlagCaller33() {
    global $name, $value, $flag, $call;
    $part = 'captured'; $value = $part . '-value';
    $name = 'NullFlagThrow33'; $flag = null; $call = 'define'; $result = 99;
    set_error_handler('stopNullFlag33');
    try {
        $result = $call(value: $value, case_insensitive: $flag, constant_name: $name);
        echo 'BAD';
    } catch (Exception $e) {
        $trace = $e->getTrace();
        echo $name, '|', $value, '|', $flag === true ? 'T' : 'F';
        echo '|', $call, '|', $result, '|', $e->getMessage();
        echo '|', $trace[0]['function'], '|', $trace[1]['function'];
        echo '|', $trace[1]['args'][0] === 'NullFlagThrow33' ? 'N' : 'BAD';
        echo '|', $trace[1]['args'][1] === 'captured-value' ? 'V' : 'BAD';
        echo '|', $trace[1]['args'][2] === null ? 'N' : 'BAD';
        echo '|', $trace[2]['function'];
        echo '|', defined('NullFlagThrow33') ? 'T' : 'F';
        echo '|', defined('changed') ? 'T' : 'F';
        echo '|', constant('NullFlagSibling33');
    } finally {
        restore_error_handler();
        echo '|Z';
    }
}
echo 'B|';
rawNullFlagCaller33();
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
