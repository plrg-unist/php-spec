#!/usr/bin/env python3
"""A NaN-name conversion handler throws before duplicate registration reporting."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'runtime-nan-name-first-warning-throw-cancels-duplicate': br'''<?php
function throwNaNName46($level, $message) {
    global $name, $candidate, $flag, $call, $count, $pending;
    echo 'H|', $level, '|', $message, '|'; $count++;
    ini_set('precision', '1');
    define('NaNNameSibling46', 977);
    $name = 2.5; $candidate = 997; $flag = true; $call = 'constant';
    $pending = new Exception('nan-name-before-body'); throw $pending;
}
function nanNameCaller46() {
    global $name, $candidate, $flag, $call, $count, $pending;
    $infinity = INF; $name = $infinity - $infinity; $candidate = 983;
    echo $name !== $name ? 'R|' : 'BAD';
    $flag = false; $call = 'define'; $count = 0; $pending = null; $result = 99;
    set_error_handler('throwNaNName46');
    try {
        $result = $call(case_insensitive: $flag, value: $candidate, constant_name: $name);
        echo 'BAD';
    } catch (Exception $e) {
        $trace = $e->getTrace(); $nan = constant('NAN');
        echo $count, '|', $result, '|', $e === $pending ? 'I' : 'BAD';
        echo '|', $e->getPrevious() === null ? 'P' : 'BAD';
        echo '|', $name === 2.5 ? 'D' : 'BAD', '|', $candidate, '|', $flag === true ? 'T' : 'BAD', '|', $call;
        echo '|', $trace[1]['args'][0] !== $trace[1]['args'][0] ? 'N' : 'BAD';
        echo '|', $trace[1]['args'][1] === 983 ? 'V' : 'BAD';
        echo '|', $trace[1]['args'][2] === false ? 'F' : 'BAD';
        echo '|', $nan !== $nan ? 'B' : 'BAD', '|', constant('NaNNameSibling46');
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; nanNameCaller46();
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
