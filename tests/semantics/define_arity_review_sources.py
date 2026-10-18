#!/usr/bin/env python3
"""A selected five-argument define() fails before its true-flag warning or body."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-five-argument-define-count-before-true-flag-body': br'''<?php
function defineArityLast49() {
    global $call, $name, $candidate, $flag, $firstExtra, $lastExtra, $effects;
    echo 'E|'; $effects++;
    $saved = $lastExtra;
    $call = 'constant'; $name = 'after-name'; $candidate = 'after-candidate';
    $flag = false; $firstExtra = 'after-first'; $lastExtra = 'after-last';
    return $saved;
}
function defineArityReviewCaller49() {
    global $call, $name, $candidate, $flag, $firstExtra, $lastExtra, $effects;
    $call = 'DeFiNe'; $part = 'captured';
    $name = $part . '-name49'; $candidate = $part . '-candidate49';
    $flag = true; $firstExtra = 1079; $lastExtra = $part . '-last49';
    $effects = 0; $result = 99;
    try {
        $result = $call($name, $candidate, $flag, $firstExtra, defineArityLast49());
        echo 'BAD';
    } catch (ArgumentCountError $e) {
        $trace = $e->getTrace();
        echo $e->getMessage(), '|', $e->getLine(), '|', $result, '|', $effects;
        echo '|', $call, '|', $name, '|', $candidate, '|', $flag === false ? 'F' : 'BAD';
        echo '|', $firstExtra, '|', $lastExtra, '|', $trace[0]['function'];
        echo '|', $trace[0]['args'][0] === 'captured-name49' ? 'N' : 'BAD';
        echo '|', $trace[0]['args'][1] === 'captured-candidate49' ? 'V' : 'BAD';
        echo '|', $trace[0]['args'][2] === true ? 'T' : 'BAD';
        echo '|', $trace[0]['args'][3] === 1079 ? 'I' : 'BAD';
        echo '|', $trace[0]['args'][4] === 'captured-last49' ? 'S' : 'BAD';
        echo '|', $trace[1]['function'], '|', $e->getPrevious() === null ? 'P' : 'BAD';
        echo '|', defined('captured-name49') ? 'BAD' : 'A';
    } finally { echo '|Z'; }
}
echo 'B|'; defineArityReviewCaller49();
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
