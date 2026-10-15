#!/usr/bin/env python3
"""Malformed class-like define names fail before any ignored-flag handler."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'request-class-like-spellings-retain-raw-arguments': br'''<?php
function unexpectedClassNameHandler36($level, $message) {
    global $warnings;
    $warnings++;
    echo 'BAD-H|';
    return false;
}
function malformedDefineNames36() {
    global $warnings;
    $part = ':'; $name = $part . ':';
    $valuePart = 'captured'; $candidate = $valuePart . '-candidate';
    $call = 'define'; $flag = true; $result = 99; $warnings = 0;
    set_error_handler('unexpectedClassNameHandler36');
    try {
        $result = $call($name, $candidate, $flag);
        echo 'BAD-A';
    } catch (ValueError $e) {
        $trace = $e->getTrace();
        echo 'A|', $e->getMessage(), '|', $e->getLine();
        echo '|', $e->getPrevious() === null ? 'P' : 'D';
        echo '|', $trace[0]['function'];
        echo '|', $trace[0]['args'][0] === '::' ? 'N' : 'D';
        echo '|', $trace[0]['args'][1] === 'captured-candidate' ? 'V' : 'D';
        echo '|', $trace[0]['args'][2] === true ? 'T' : 'D';
        echo '|', $result;
    }
    $prefix = 'A:'; $name = $prefix . '::B'; $result = 101;
    try {
        $result = define(value: 313, case_insensitive: false, constant_name: $name);
        echo 'BAD-B';
    } catch (ValueError $e) {
        $trace = $e->getTrace();
        echo '|B|', $e->getMessage(), '|', $e->getLine();
        echo '|', $e->getPrevious() === null ? 'P' : 'D';
        echo '|', $trace[0]['function'];
        echo '|', $trace[0]['args'][0] === 'A:::B' ? 'N' : 'D';
        echo '|', $trace[0]['args'][1] === 313 ? 'V' : 'D';
        echo '|', $trace[0]['args'][2] === false ? 'F' : 'D';
        echo '|', $result;
    }
    restore_error_handler();
    echo '|', $warnings, '|', $name, '|', $candidate, '|', $call;
}
echo 'B|';
malformedDefineNames36();
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
