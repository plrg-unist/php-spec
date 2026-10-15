#!/usr/bin/env python3
"""False-valued quiet flags stay raw while class-like define names fail."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'negative-zero-and-request-zero-flags-stay-raw': br'''<?php
function forbiddenFalseClassFlag37($level, $message) {
    global $warnings;
    $warnings++;
    echo 'BAD-H|';
    return true;
}
function falseClassFlags37() {
    global $warnings;
    $warnings = 0; $result = 99;
    set_error_handler('forbiddenFalseClassFlag37');
    try {
        $result = define('Negative::Flag37', 317, -0.0);
        echo 'BAD-A';
    } catch (ValueError $e) {
        $trace = $e->getTrace(); $raw = $trace[0]['args'][2];
        echo 'A|', $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
        echo '|', $trace[0]['args'][0] === 'Negative::Flag37' ? 'N' : 'BAD';
        echo '|', $trace[0]['args'][1] === 317 ? 'V' : 'BAD';
        echo '|', $raw === -0.0 ? 'D' : 'BAD', '|', $raw;
        echo '|', $e->getPrevious() === null ? 'P' : 'BAD', '|', $result;
    }
    $left = '00'; $mask = '0'; $flag = $left & $mask;
    $namePart = 'Zero'; $name = $namePart . '::Flag37';
    $valuePart = 'request'; $candidate = $valuePart . '-value';
    $call = 'define'; $result = 101;
    try {
        $result = $call(value: $candidate, case_insensitive: $flag, constant_name: $name);
        echo 'BAD-B';
    } catch (ValueError $e) {
        $trace = $e->getTrace(); $raw = $trace[0]['args'][2];
        echo '|B|', $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
        echo '|', $trace[0]['args'][0] === 'Zero::Flag37' ? 'N' : 'BAD';
        echo '|', $trace[0]['args'][1] === 'request-value' ? 'V' : 'BAD';
        echo '|', $raw === '0' ? 'S' : 'BAD', '|', $raw;
        echo '|', $e->getPrevious() === null ? 'P' : 'BAD', '|', $result;
    }
    restore_error_handler();
    echo '|', $warnings, '|', $flag === '0' ? 'Z' : 'BAD', '|', $name, '|', $candidate;
}
echo 'B|';
falseClassFlags37();
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
