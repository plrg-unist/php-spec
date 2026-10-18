#!/usr/bin/env python3
"""A malformed class spelling is rejected only after the name conversion returns."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-stringable-malformed-class-name-preserves-converted-captures': br'''<?php
class DefineStringClassReview57 {
    public function __toString(): string {
        global $call, $name, $value, $flag, $calls;
        echo 'S|'; $calls++; define('SOURCE57PEER', 1657);
        $call = 'constant'; $name = 'cast-name57'; $value = 'cast-value57'; $flag = true;
        $part = 'A'; return $part . ':::B';
    }
}
function defineStringClassReviewValue57() {
    global $call, $name, $value, $effects;
    echo 'V|'; $effects++; $earlier = $value;
    $call = 'defined'; $name = 'argument-name57'; return $earlier;
}
function defineStringClassReviewCaller57() {
    global $call, $name, $value, $flag, $calls, $effects;
    $call = 'DeFiNe'; $name = new DefineStringClassReview57(); $keep = $name;
    $part = 'captured'; $value = $part . '-value57'; $flag = false;
    $calls = 0; $effects = 0; $result = 99;
    try {
        $result = $call($name, defineStringClassReviewValue57(), $flag);
        echo 'BAD';
    } catch (ValueError $e) {
        $trace = $e->getTrace();
        echo $e->getMessage(), '|', $trace[0]['function'];
        echo '|', $trace[0]['args'][0] === 'A:::B' ? 'N' : 'BAD';
        echo '|', $trace[0]['args'][1] === 'captured-value57' ? 'V' : 'BAD';
        echo '|', $trace[0]['args'][2] === false ? 'F' : 'BAD';
        echo '|', $trace[1]['function'], '|', $result, '|', $calls, '|', $effects;
        echo '|', $call, '|', $name, '|', $value, '|', $flag === true ? 'T' : 'BAD';
        echo '|', constant('SOURCE57PEER');
    } finally { echo '|Z'; }
}
echo 'B|'; defineStringClassReviewCaller57();
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
