#!/usr/bin/env python3
"""A selected four-argument constant() count error precedes class-name lookup."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-class-like-query-count-before-lookup-and-one-arg-recovery': br'''<?php
function queryExcessLast50() {
    global $call, $name, $extra, $flag, $lastExtra, $effects;
    echo 'E|'; $effects++; $saved = $lastExtra;
    $call = 'defined'; $name = 'TRUE'; $extra = 'after-extra50';
    $flag = true; $lastExtra = 'after-last50';
    return $saved;
}
function queryExcessReviewCaller50() {
    global $call, $name, $extra, $flag, $lastExtra, $effects;
    $call = 'CoNsTaNt'; $part = 'MissingArity50'; $name = $part . '::VALUE';
    $part = 'captured'; $extra = $part . '-extra50';
    $flag = false; $lastExtra = $part . '-last50'; $effects = 0; $result = 99;
    try {
        $result = $call($name, $extra, $flag, queryExcessLast50());
        echo 'BAD';
    } catch (ArgumentCountError $e) {
        $trace = $e->getTrace();
        echo $e->getMessage(), '|', $e->getLine(), '|', $result, '|', $effects;
        echo '|', $call, '|', $name, '|', $extra, '|', $flag === true ? 'T' : 'BAD', '|', $lastExtra;
        echo '|', $trace[0]['function'];
        echo '|', $trace[0]['args'][0] === 'MissingArity50::VALUE' ? 'N' : 'BAD';
        echo '|', $trace[0]['args'][1] === 'captured-extra50' ? 'E' : 'BAD';
        echo '|', $trace[0]['args'][2] === false ? 'F' : 'BAD';
        echo '|', $trace[0]['args'][3] === 'captured-last50' ? 'L' : 'BAD';
        echo '|', $trace[1]['function'], '|', $e->getPrevious() === null ? 'P' : 'BAD';
        echo '|', $call($name) ? 'R' : 'BAD';
    } finally { echo '|Z'; }
}
echo 'B|'; queryExcessReviewCaller50();
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
