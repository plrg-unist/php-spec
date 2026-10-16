#!/usr/bin/env python3
"""A converted float key survives precision changes and a throwing duplicate."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'float-name-request-zero-duplicate-throw-keeps-historical-key': br'''<?php
function throwFloatFalse42($level, $message) {
    global $name, $candidate, $flag, $call, $count, $pending;
    echo 'H|', $level, '|', $message, '|'; $count++;
    ini_set('precision', '1');
    define('FloatFalseSibling42', 719);
    $name = 9.5; $candidate = 777; $flag = true; $call = 'constant';
    $pending = new Exception('float-false-duplicate'); throw $pending;
}
function floatFalseCaller42() {
    global $name, $candidate, $flag, $call, $count, $pending;
    define('2.5', 701);
    $name = 2.5; $candidate = 733;
    $left = '00'; $mask = '0'; $flag = $left & $mask;
    $call = 'define'; $count = 0; $pending = null; $result = 99;
    set_error_handler('throwFloatFalse42');
    try {
        $result = $call(case_insensitive: $flag, value: $candidate, constant_name: $name);
        echo 'BAD';
    } catch (Exception $e) {
        $trace = $e->getTrace();
        echo $count, '|', $result, '|', $e === $pending ? 'I' : 'BAD';
        echo '|', $e->getPrevious() === null ? 'P' : 'BAD';
        echo '|', $name === 9.5 ? 'D' : 'BAD', '|', $candidate;
        echo '|', $flag === true ? 'T' : 'BAD', '|', $call;
        echo '|', $trace[1]['args'][0] === '2.5' ? 'S' : 'BAD';
        echo '|', $trace[1]['args'][1] === 733 ? 'V' : 'BAD';
        echo '|', $trace[1]['args'][2] === '0' ? 'Z' : 'BAD';
        echo '|', constant('2.5'), '|', constant('FloatFalseSibling42');
        echo '|', defined('2') ? 'BAD' : 'F';
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; floatFalseCaller42();
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
