#!/usr/bin/env python3
"""A false name converts to the empty key while a request flag stays raw."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'false-name-empty-key-duplicate-keeps-raw-zero-flag': br'''<?php
function throwEmptyDuplicate40($level, $message) {
    global $warnings, $name, $candidate, $flag, $call, $pending;
    echo 'H|', $level, '|', $message, '|'; $warnings++;
    define('EmptyDuplicateSibling40', 569);
    $name = true; $candidate = 'changed-candidate'; $flag = true; $call = 'constant';
    $pending = new Exception('empty-name-duplicate');
    throw $pending;
}
function emptyDuplicateCaller40() {
    global $warnings, $name, $candidate, $flag, $call, $pending;
    define('', 557);
    $part = 'outer'; $candidate = $part . '-value40';
    $left = '00'; $mask = '0'; $flag = $left & $mask;
    $name = false; $warnings = 0; $call = 'define'; $pending = null; $result = 99;
    set_error_handler('throwEmptyDuplicate40');
    try {
        $result = $call(case_insensitive: $flag, value: $candidate, constant_name: $name);
        echo 'BAD-NORMAL|';
    } catch (Exception $e) {
        $trace = $e->getTrace();
        echo $warnings, '|', $name === true ? 'T' : 'BAD', '|', $candidate;
        echo '|', $flag === true ? 'T' : 'BAD', '|', $call, '|', $result;
        echo '|', $e->getMessage(), '|', $e === $pending ? 'I' : 'BAD';
        echo '|', $e->getPrevious() === null ? 'P' : 'BAD';
        echo '|', $trace[0]['function'], '|', $trace[1]['function'];
        echo '|', $trace[1]['args'][0] === '' ? 'E' : 'BAD';
        echo '|', $trace[1]['args'][1] === 'outer-value40' ? 'V' : 'BAD';
        echo '|', $trace[1]['args'][2] === '0' ? 'S' : 'BAD';
        echo '|', $trace[2]['function'], '|', constant(''), '|', constant('EmptyDuplicateSibling40');
    } finally {
        restore_error_handler();
        echo '|Z';
    }
}
echo 'B|';
emptyDuplicateCaller40();
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
