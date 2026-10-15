#!/usr/bin/env python3
"""A NULL flag deprecation throw cancels the later class-name body error."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'null-flag-throw-cancels-class-name-error': br'''<?php
function throwClassNull38($level, $message) {
    global $warnings, $name, $candidate, $flag, $call, $pending;
    echo 'H|', $level, '|', $message, '|'; $warnings++;
    define('ClassNullInner38', 337);
    $name = 'changed-null-name'; $candidate = 'changed-null-value';
    $flag = true; $call = 'constant';
    $pending = new Exception('null-before-body');
    throw $pending;
}
function classNullCaller38() {
    global $warnings, $name, $candidate, $flag, $call, $pending;
    $part = 'Captured'; $name = $part . '::Null38';
    $part = 'outer'; $candidate = $part . '-candidate';
    $warnings = 0; $flag = null; $call = 'define';
    $pending = null; $result = 99;
    set_error_handler('throwClassNull38');
    try {
        $result = $call(case_insensitive: $flag, value: $candidate, constant_name: $name);
        echo 'BAD-NORMAL|';
    } catch (Exception $e) {
        $trace = $e->getTrace();
        echo $warnings, '|', $name, '|', $candidate, '|', $flag === true ? 'T' : 'BAD';
        echo '|', $call, '|', $result, '|', $e->getMessage();
        echo '|', $e === $pending ? 'I' : 'BAD';
        echo '|', $e->getPrevious() === null ? 'P' : 'BAD';
        echo '|', $trace[0]['function'], '|', $trace[1]['function'];
        echo '|', $trace[1]['args'][0] === 'Captured::Null38' ? 'N' : 'BAD';
        echo '|', $trace[1]['args'][1] === 'outer-candidate' ? 'V' : 'BAD';
        echo '|', $trace[1]['args'][2] === null ? 'Z' : 'BAD';
        echo '|', $trace[2]['function'], '|', constant('ClassNullInner38');
        echo '|', defined('changed-null-name') ? 'BAD' : 'F';
    } finally {
        restore_error_handler();
        echo '|Z';
    }
}
echo 'B|';
classNullCaller38();
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
