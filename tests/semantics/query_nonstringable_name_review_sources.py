#!/usr/bin/env python3
"""A failed query cast ignores an ordinary toString method and keeps its receiver."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-nonstringable-defined-does-not-call-ordinary-string-method': br'''<?php
class QueryNonStringReview54 {
    public function toString() {
        global $methodCalls;
        $methodCalls++; echo 'BAD'; return 'TRUE';
    }
}
function queryNonStringReviewArgument54() {
    global $call, $name, $effects;
    echo 'A|'; $effects++; $original = $name;
    $call = 'constant'; $name = 'argument-live54'; return $original;
}
function queryNonStringReviewCaller54() {
    global $call, $name, $effects, $methodCalls;
    $call = 'DeFiNeD'; $name = new QueryNonStringReview54(); $keep = $name;
    $effects = 0; $methodCalls = 0; $result = 99;
    try {
        $result = $call(queryNonStringReviewArgument54());
        echo 'BAD';
    } catch (TypeError $e) {
        $trace = $e->getTrace();
        echo $e->getMessage(), '|', $result, '|', $effects, '|', $methodCalls;
        echo '|', $call, '|', $name;
        echo '|', $trace[0]['function'];
        echo '|', $trace[0]['args'][0] === $keep ? 'O' : 'BAD';
        echo '|', $trace[1]['function'], '|', $e->getPrevious() === null ? 'P' : 'BAD';
    } finally { echo '|Z'; }
    $call = 'DeFiNeD';
    echo '|', $call('TRUE') ? 'T' : 'BAD', '|', $result;
}
echo 'B|'; queryNonStringReviewCaller54();
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
