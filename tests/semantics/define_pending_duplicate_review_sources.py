#!/usr/bin/env python3
"""Observe a pending scalar-flag duplicate against an already installed row."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'scalar-flag-pending-duplicate-keeps-existing-row': br'''<?php
function keepScalarPendingDup34($level, $message) {
    global $warnings, $name, $candidate, $flag, $call, $pending;
    echo 'H|', $level, '|'; $warnings++;
    if ($warnings === 1) {
        $name = 'changed'; $candidate = 999; $flag = 0; $call = 'defined';
        $pending = new Exception('scalar-first');
        throw $pending;
    }
    echo 'SECOND|';
    return false;
}
function scalarPendingDupCaller34() {
    global $warnings, $name, $candidate, $flag, $call, $pending;
    $part = 'captured'; $candidate = $part . '-candidate';
    $flagPart = 'f'; $flag = $flagPart . 'alse';
    $warnings = 0; $name = 'ScalarPendingDup34'; $call = 'define';
    $pending = null; $result = 99;
    set_error_handler('keepScalarPendingDup34');
    try {
        $result = $call(case_insensitive: $flag, constant_name: $name, value: $candidate);
        echo 'NORMAL|';
    } catch (Exception $e) {
        $trace = $e->getTrace();
        echo $warnings, '|', $name, '|', $candidate, '|', $flag === 0 ? 'I' : 'D';
        echo '|', $call, '|', $result, '|', $e->getMessage();
        echo '|', $e === $pending ? 'I' : 'D';
        echo '|', $e->getPrevious() === null ? 'N' : 'P';
        echo '|', $trace[0]['function'], '|', $trace[1]['function'];
        echo '|', $trace[1]['args'][0] === 'ScalarPendingDup34' ? 'N' : 'D';
        echo '|', $trace[1]['args'][1] === 'captured-candidate' ? 'V' : 'D';
        echo '|', $trace[1]['args'][2] === 'false' ? 'S' : 'D';
        echo '|', $trace[2]['function'], '|', constant('ScalarPendingDup34');
        echo '|', defined('changed') ? 'T' : 'F';
    } finally {
        restore_error_handler();
        echo '|Z';
    }
}
define('ScalarPendingDup34', 283);
echo 'B|';
scalarPendingDupCaller34();
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
