#!/usr/bin/env python3
"""A throwing NaN boolean receive cancels outer define after callback effects."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'nan-flag-first-warning-throw-keeps-inner-binding': br'''<?php
function throwNaNReceive35($level, $message) {
    global $warnings, $name, $candidate, $flag, $call, $pending;
    echo 'H|', $level, '|', $message, '|'; $warnings++;
    define('NaNReceiveInner35', 307);
    $name = 'changed'; $candidate = 'changed-value'; $flag = 0; $call = 'defined';
    $pending = new Exception('first-nan');
    throw $pending;
}
function nanReceiveCaller35() {
    global $warnings, $name, $candidate, $flag, $call, $pending;
    $part = 'captured'; $candidate = $part . '-candidate';
    $warnings = 0; $name = 'NaNReceiveInner35'; $flag = NAN; $call = 'define';
    $pending = null; $result = 99;
    set_error_handler('throwNaNReceive35');
    try {
        $result = $call(case_insensitive: $flag, value: $candidate, constant_name: $name);
        echo 'NORMAL|';
    } catch (Exception $e) {
        $trace = $e->getTrace();
        echo $warnings, '|', $name, '|', $candidate, '|', $flag === 0 ? 'I' : 'D';
        echo '|', $call, '|', $result, '|', $e->getMessage();
        echo '|', $e === $pending ? 'I' : 'D';
        echo '|', $e->getPrevious() === null ? 'N' : 'P';
        echo '|', $trace[0]['function'], '|', $trace[1]['function'];
        echo '|', $trace[1]['args'][0] === 'NaNReceiveInner35' ? 'N' : 'D';
        echo '|', $trace[1]['args'][1] === 'captured-candidate' ? 'V' : 'D';
        echo '|', $trace[1]['args'][2] !== $trace[1]['args'][2] ? 'A' : 'D';
        echo '|', $trace[2]['function'], '|', constant('NaNReceiveInner35');
        echo '|', defined('changed') ? 'T' : 'F';
    } finally {
        restore_error_handler();
        echo '|Z';
    }
}
echo 'B|';
nanReceiveCaller35();
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
