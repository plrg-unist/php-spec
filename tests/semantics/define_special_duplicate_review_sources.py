#!/usr/bin/env python3
"""A mixed-case special-name duplicate survives a supplied handler throw."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'request-special-null-duplicate-throw-preserves-specials': br'''<?php
function throwSpecialDuplicate44($level, $message) {
    global $name, $candidate, $flag, $call, $count, $pending;
    echo 'H|', $level, '|', $message, '|'; $count++;
    define('SpecialDuplicateSibling44', 847);
    $name = 'true'; $candidate = 997; $flag = true; $call = 'constant';
    $pending = new Exception('special-duplicate'); throw $pending;
}
function specialDuplicateCaller44() {
    global $name, $candidate, $flag, $call, $count, $pending;
    $part = 'nU'; $name = $part . 'lL'; $candidate = 863;
    $flag = false; $call = 'define'; $count = 0; $pending = null; $result = 99;
    set_error_handler('throwSpecialDuplicate44');
    try {
        $result = $call(case_insensitive: $flag, value: $candidate, constant_name: $name);
        echo 'BAD';
    } catch (Exception $e) {
        $trace = $e->getTrace();
        echo $count, '|', $result, '|', $e === $pending ? 'I' : 'BAD';
        echo '|', $e->getPrevious() === null ? 'P' : 'BAD';
        echo '|', $name, '|', $candidate, '|', $flag === true ? 'T' : 'BAD', '|', $call;
        echo '|', $trace[1]['args'][0] === 'nUlL' ? 'S' : 'BAD';
        echo '|', $trace[1]['args'][1] === 863 ? 'V' : 'BAD';
        echo '|', $trace[1]['args'][2] === false ? 'F' : 'BAD';
        echo '|', constant('nUlL') === null ? 'N' : 'BAD';
        echo '|', constant('TRUE') === true ? 'T' : 'BAD';
        echo '|', constant('FaLsE') === false ? 'F' : 'BAD';
        echo '|', constant('SpecialDuplicateSibling44');
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; specialDuplicateCaller44();
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
