#!/usr/bin/env python3
"""A selected defined() count error keeps raw null and its captured extra input."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-mixed-case-defined-count-before-null-conversion': br'''<?php
function queryArityExtra48() {
    global $call, $name, $extra, $effects;
    echo 'E|'; $effects++;
    $saved = $extra;
    $call = 'constant'; $name = 'TRUE'; $extra = 'after-extra';
    return $saved;
}
function queryArityReviewCaller48() {
    global $call, $name, $extra, $effects;
    $call = 'DeFiNeD'; $name = null; $part = 'request'; $extra = $part . '-extra';
    $effects = 0; $result = 99;
    try {
        $result = $call($name, queryArityExtra48());
        echo 'BAD';
    } catch (ArgumentCountError $e) {
        $trace = $e->getTrace();
        echo $e->getMessage(), '|', $e->getLine(), '|', $result, '|', $effects;
        echo '|', $call, '|', $name, '|', $extra;
        echo '|', $trace[0]['function'], '|', $trace[0]['args'][0] === null ? 'N' : 'BAD';
        echo '|', $trace[0]['args'][1] === 'request-extra' ? 'S' : 'BAD';
        echo '|', $trace[1]['function'], '|', $e->getPrevious() === null ? 'P' : 'BAD';
    } finally { echo '|Z'; }
}
echo 'B|'; queryArityReviewCaller48();
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
