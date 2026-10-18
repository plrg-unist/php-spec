#!/usr/bin/env python3
"""A failed define-name cast ignores toString after both later arguments finish."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-nonstringable-define-before-captured-true-flag-reception': br'''<?php
class DefineNonStringReview56 {
    public function toString() {
        global $methodCalls;
        $methodCalls++; echo 'BAD'; return 'WRONG56';
    }
}
function defineNonStringReviewValue56() {
    global $call, $name, $value, $effects;
    echo 'V|'; $effects++; $earlier = $value;
    $call = 'defined'; $name = 'value-name56'; return $earlier;
}
function defineNonStringReviewFlag56() {
    global $call, $name, $value, $flag, $effects;
    echo 'F|'; $effects++; $earlier = $flag;
    $call = 'constant'; $name = 'flag-name56'; $value = 'flag-value56'; $flag = false;
    return $earlier;
}
function defineNonStringReviewCaller56() {
    global $call, $name, $value, $flag, $effects, $methodCalls;
    $call = 'DeFiNe'; $name = new DefineNonStringReview56(); $keep = $name;
    $part = 'captured'; $value = $part . '-value56'; $flag = true;
    $effects = 0; $methodCalls = 0; $result = 99;
    try {
        $result = $call($name, defineNonStringReviewValue56(), defineNonStringReviewFlag56());
        echo 'BAD';
    } catch (TypeError $e) {
        $trace = $e->getTrace();
        echo $e->getMessage(), '|', $result, '|', $effects, '|', $methodCalls;
        echo '|', $call, '|', $name, '|', $value, '|', $flag === false ? 'F' : 'BAD';
        echo '|', $trace[0]['function'];
        echo '|', $trace[0]['args'][0] === $keep ? 'O' : 'BAD';
        echo '|', $trace[0]['args'][1] === 'captured-value56' ? 'V' : 'BAD';
        echo '|', $trace[0]['args'][2] === true ? 'T' : 'BAD';
        echo '|', $trace[1]['function'];
    } finally { echo '|Z'; }
    $call = 'DeFiNeD';
    echo '|', $call('TRUE') ? 'T' : 'BAD', '|', $result;
}
echo 'B|'; defineNonStringReviewCaller56();
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
