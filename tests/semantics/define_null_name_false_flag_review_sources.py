#!/usr/bin/env python3
"""A first NULL-name deprecation throw prevents empty-key registration."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'null-name-false-request-flag-first-throw-leaves-empty-key-absent': br'''<?php
function throwNullFalseName41($level, $message) {
    global $warnings, $name, $candidate, $flag, $call, $pending;
    echo 'H|', $level, '|', $message, '|'; $warnings++;
    define('NullFalseInner41', 617);
    $name = 'changed-null-name'; $candidate = 'changed-candidate';
    $flag = true; $call = 'constant';
    $pending = new Exception('null-name-before-registration');
    throw $pending;
}
function nullFalseCaller41() {
    global $warnings, $name, $candidate, $flag, $call, $pending;
    $part = 'outer'; $candidate = $part . '-value41';
    $left = '00'; $mask = '0'; $flag = $left & $mask;
    $name = null; $warnings = 0; $call = 'define'; $pending = null; $result = 99;
    set_error_handler('throwNullFalseName41');
    try {
        $result = $call(case_insensitive: $flag, value: $candidate, constant_name: $name);
        echo 'BAD-NORMAL|';
    } catch (Exception $e) {
        $trace = $e->getTrace();
        echo $warnings, '|', $name, '|', $candidate, '|', $flag === true ? 'T' : 'BAD';
        echo '|', $call, '|', $result, '|', $e->getMessage();
        echo '|', $e === $pending ? 'I' : 'BAD', '|', $e->getPrevious() === null ? 'P' : 'BAD';
        echo '|', $trace[0]['function'], '|', $trace[1]['function'];
        echo '|', $trace[1]['args'][0] === null ? 'N' : 'BAD';
        echo '|', $trace[1]['args'][1] === 'outer-value41' ? 'V' : 'BAD';
        echo '|', $trace[1]['args'][2] === '0' ? 'S' : 'BAD';
        echo '|', $trace[2]['function'], '|', constant('NullFalseInner41');
        echo '|', defined('') ? 'BAD' : 'F';
    } finally {
        restore_error_handler();
        echo '|Z';
    }
}
echo 'B|';
nullFalseCaller41();
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
