#!/usr/bin/env python3
"""A startup NAN duplicate keeps its builtin value through a throwing handler."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'request-startup-nan-duplicate-throw-preserves-builtin': br'''<?php
function throwStartupDuplicate43($level, $message) {
    global $name, $candidate, $flag, $call, $count, $pending;
    echo 'H|', $level, '|', $message, '|'; $count++;
    define('StartupDuplicateSibling43', 811);
    $name = 'PHP_INT_SIZE'; $candidate = 997; $flag = true; $call = 'constant';
    $pending = new Exception('startup-duplicate'); throw $pending;
}
function startupDuplicateCaller43() {
    global $name, $candidate, $flag, $call, $count, $pending;
    $part = 'N'; $name = $part . 'AN'; $candidate = 823;
    $flag = false; $call = 'define'; $count = 0; $pending = null; $result = 99;
    set_error_handler('throwStartupDuplicate43');
    try {
        $result = $call(case_insensitive: $flag, value: $candidate, constant_name: $name);
        echo 'BAD';
    } catch (Exception $e) {
        $trace = $e->getTrace(); $nan = constant('NAN');
        echo $count, '|', $result, '|', $e === $pending ? 'I' : 'BAD';
        echo '|', $e->getPrevious() === null ? 'P' : 'BAD';
        echo '|', $name, '|', $candidate, '|', $flag === true ? 'T' : 'BAD', '|', $call;
        echo '|', $trace[1]['args'][0] === 'NAN' ? 'S' : 'BAD';
        echo '|', $trace[1]['args'][1] === 823 ? 'V' : 'BAD';
        echo '|', $trace[1]['args'][2] === false ? 'F' : 'BAD';
        echo '|', $nan !== $nan ? 'N' : 'BAD', '|', constant('StartupDuplicateSibling43');
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; startupDuplicateCaller43();
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
