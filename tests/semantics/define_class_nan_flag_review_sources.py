#!/usr/bin/env python3
"""A runtime NaN flag Warning throw cancels the later class-name body error."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'runtime-nan-flag-throw-cancels-class-name-error': br'''<?php
function throwClassNaN39($level, $message) {
    global $warnings, $name, $candidate, $flag, $call, $pending;
    echo 'H|', $level, '|', $message, '|'; $warnings++;
    define('ClassNaNInner39', 353);
    $name = 'changed-nan-name'; $candidate = 'changed-nan-value';
    $flag = 0; $call = 'constant';
    $pending = new Exception('nan-before-class');
    throw $pending;
}
function classNaNCaller39() {
    global $warnings, $name, $candidate, $flag, $call, $pending;
    $part = 'Captured'; $name = $part . '::NaN39';
    $part = 'captured'; $candidate = $part . '-value39';
    $infinity = INF; $flag = $infinity - $infinity;
    $warnings = 0; $call = 'define'; $pending = null; $result = 99;
    set_error_handler('throwClassNaN39');
    try {
        $result = $call(case_insensitive: $flag, value: $candidate, constant_name: $name);
        echo 'BAD-NORMAL|';
    } catch (Exception $e) {
        $trace = $e->getTrace();
        echo $warnings, '|', $name, '|', $candidate, '|', $flag === 0 ? 'I' : 'BAD';
        echo '|', $call, '|', $result, '|', $e->getMessage();
        echo '|', $e === $pending ? 'I' : 'BAD';
        echo '|', $e->getPrevious() === null ? 'P' : 'BAD';
        echo '|', $trace[0]['function'], '|', $trace[1]['function'];
        echo '|', $trace[1]['args'][0] === 'Captured::NaN39' ? 'N' : 'BAD';
        echo '|', $trace[1]['args'][1] === 'captured-value39' ? 'V' : 'BAD';
        echo '|', $trace[1]['args'][2] !== $trace[1]['args'][2] ? 'A' : 'BAD';
        echo '|', $trace[2]['function'], '|', constant('ClassNaNInner39');
        echo '|', defined('changed-nan-name') ? 'BAD' : 'F';
    } finally {
        restore_error_handler();
        echo '|Z';
    }
}
echo 'B|';
classNaNCaller39();
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
