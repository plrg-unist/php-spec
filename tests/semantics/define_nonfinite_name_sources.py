#!/usr/bin/env python3
"""Native-first infinite define names and strict NaN name rejection."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'infinite-names-startup-duplicates-and-negative-fresh-key': br'''<?php
echo 'B|';
echo define(INF, 901) ? 'BAD' : 'F', '|', constant('INF') === INF ? 'I' : 'BAD';
echo '|', define(INF, 907, false) ? 'BAD' : 'F', '|', constant('INF') === INF ? 'I' : 'BAD';
echo '|', define(-INF, 911, false) ? 'T' : 'BAD', '|', constant('-INF');
''',
    'captured-infinite-name-before-request-value-and-live-effects': br'''<?php
function infiniteValue45() {
    global $name, $candidate, $flag, $call;
    echo 'V|'; $name = 2.5; $candidate = 997; $flag = true; $call = 'constant';
    $part = 'outer'; return $part . '-candidate45';
}
function infiniteName45() {
    global $name, $flag, $call;
    echo 'N|'; $name = 9.5; $flag = true; $call = 'defined'; return INF;
}
function returnInfinite45($level, $message) {
    global $name, $candidate, $flag, $call, $count;
    echo 'H|', $level, '|', $message, '|'; $count++;
    define('InfiniteSibling45', 929);
    $name = 7.5; $candidate = 991; $flag = true; $call = 'constant'; return false;
}
function infiniteCaller45() {
    global $name, $candidate, $flag, $call, $count;
    $name = 0; $candidate = 0; $flag = false; $call = 'define'; $count = 0; $result = 99;
    set_error_handler('returnInfinite45');
    try {
        $result = $call(case_insensitive: $flag, value: infiniteValue45(), constant_name: infiniteName45());
        echo $result === false ? 'F' : 'BAD', '|', $count;
        echo '|', constant('INF') === INF ? 'I' : 'BAD', '|', constant('InfiniteSibling45');
        echo '|', $name === 7.5 ? 'D' : 'BAD', '|', $candidate;
        echo '|', $flag === true ? 'T' : 'BAD', '|', $call;
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; infiniteCaller45();
''',
    'strict-nan-name-rejected-before-string-conversion-after-effects': br'''<?php
declare(strict_types=1);
function strictInfiniteValue45() { global $name, $flag, $call; echo 'V|'; $name = INF; $flag = true; $call = 'constant'; return 947; }
function strictInfiniteName45() { global $name, $call; echo 'N|'; $name = 3.5; $call = 'defined'; return NAN; }
function forbiddenInfinite45($level, $message) { echo 'BAD-H|'; return true; }
$flag = false; $call = 'define'; $result = 99;
set_error_handler('forbiddenInfinite45');
echo 'B|';
try {
    $result = $call(case_insensitive: $flag, value: strictInfiniteValue45(), constant_name: strictInfiniteName45());
    echo 'BAD';
} catch (TypeError $e) {
    $trace = $e->getTrace();
    echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0] !== $trace[0]['args'][0] ? 'N' : 'BAD';
    echo '|', $trace[0]['args'][1], '|', $trace[0]['args'][2] === false ? 'F' : 'BAD';
    echo '|', $e->getPrevious() === null ? 'P' : 'BAD';
}
restore_error_handler();
echo '|', $name === 3.5 ? 'D' : 'BAD', '|', $flag === true ? 'T' : 'BAD', '|', $call, '|', $result;
''',
}
family.BASELINE = ('scalar define publication', b'B|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
