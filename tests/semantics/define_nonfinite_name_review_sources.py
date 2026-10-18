#!/usr/bin/env python3
"""An infinite name converts before a throwing startup-duplicate handler."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'infinite-name-duplicate-throw-keeps-converted-trace': br'''<?php
function throwNonfiniteDuplicate45($level, $message) {
    global $name, $candidate, $flag, $call, $count, $pending;
    echo 'H|', $level, '|', $message, '|'; $count++;
    ini_set('precision', '1');
    define('NonfiniteDuplicateSibling45', 919);
    $name = 2.5; $candidate = 997; $flag = true; $call = 'constant';
    $pending = new Exception('nonfinite-duplicate'); throw $pending;
}
function nonfiniteDuplicateCaller45() {
    global $name, $candidate, $flag, $call, $count, $pending;
    $name = INF; $candidate = 907;
    echo $name === INF ? 'R|' : 'BAD';
    $flag = false; $call = 'define'; $count = 0; $pending = null; $result = 99;
    set_error_handler('throwNonfiniteDuplicate45');
    try {
        $result = $call(case_insensitive: $flag, value: $candidate, constant_name: $name);
        echo 'BAD';
    } catch (Exception $e) {
        $trace = $e->getTrace();
        echo $count, '|', $result, '|', $e === $pending ? 'I' : 'BAD';
        echo '|', $e->getPrevious() === null ? 'P' : 'BAD';
        echo '|', $name === 2.5 ? 'D' : 'BAD', '|', $candidate, '|', $flag === true ? 'T' : 'BAD', '|', $call;
        echo '|', $trace[1]['args'][0] === 'INF' ? 'S' : 'BAD';
        echo '|', $trace[1]['args'][1] === 907 ? 'V' : 'BAD';
        echo '|', $trace[1]['args'][2] === false ? 'F' : 'BAD';
        echo '|', constant('INF') === INF ? 'I' : 'BAD';
        echo '|', constant('NonfiniteDuplicateSibling45');
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; nonfiniteDuplicateCaller45();
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
